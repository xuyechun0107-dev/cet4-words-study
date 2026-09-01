param(
    [Parameter(Mandatory = $true)]
    [string]$Workspace,
    [Parameter(Mandatory = $true)]
    [string]$BuildRoot,
    [string]$RemoteHostName = "aoke@192.168.0.103",
    [string]$RemoteAudioRoot = "/home/aoke/apps/cet4-study/audio/v1",
    [switch]$MaleOnly
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = Join-Path $BuildRoot "site-packages"
$env:OMP_NUM_THREADS = "6"
$env:OMP_WAIT_POLICY = "PASSIVE"

$python = (Get-Command python).Source
$generator = Join-Path $Workspace "generate_recorded_audio.py"
$normalizer = Join-Path $Workspace "normalize_recorded_audio.py"
$model = Join-Path $BuildRoot "kokoro-v1.0.fp16.onnx"
$voicesFile = Join-Path $BuildRoot "voices-v1.0.bin"
$outputRoot = Join-Path $BuildRoot "output"
$logRoot = Join-Path $BuildRoot "logs"
$runId = Get-Date -Format "yyyyMMdd-HHmmss"

[IO.Directory]::CreateDirectory($outputRoot) | Out-Null
[IO.Directory]::CreateDirectory($logRoot) | Out-Null

function Write-BuildStatus {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -LiteralPath (Join-Path $logRoot "build-status.log") -Value $line -Encoding UTF8
}

function Start-AudioWorker {
    param(
        [string]$Name,
        [string]$SourceMode,
        [string[]]$Voices
    )

    $stdout = Join-Path $logRoot "$Name.$runId.stdout.log"
    $stderr = Join-Path $logRoot "$Name.$runId.stderr.log"
    $arguments = @(
        $generator,
        "--workspace", $Workspace,
        "--model", $model,
        "--voices-file", $voicesFile,
        "--output", $outputRoot,
        "--source-mode", $SourceMode,
        "--progress-every", "100",
        "--voices"
    ) + $Voices

    $process = Start-Process -FilePath $python `
        -ArgumentList ($arguments | ForEach-Object { '"' + $_ + '"' }) `
        -WorkingDirectory $Workspace `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru

    Write-BuildStatus "Started $Name (PID $($process.Id)): $($Voices -join ', ')"
    return [pscustomobject]@{
        Name = $Name
        Process = $process
        Voices = $Voices
        Uploaded = $false
    }
}

function Publish-Voice {
    param([string]$Voice)

    $voiceRoot = Join-Path (Join-Path $outputRoot "v1") $Voice
    if (-not (Test-Path -LiteralPath $voiceRoot -PathType Container)) {
        throw "Generated voice directory is missing: $voiceRoot"
    }

    Write-BuildStatus "Normalizing $Voice before upload"
    & $python $normalizer --root $voiceRoot --progress-every 250
    if ($LASTEXITCODE -ne 0) {
        throw "loudness normalization failed for $Voice"
    }

    Write-BuildStatus "Uploading $Voice to $RemoteHostName"
    & scp -o BatchMode=yes -o ConnectTimeout=20 -r -- $voiceRoot "${RemoteHostName}:${RemoteAudioRoot}/"
    if ($LASTEXITCODE -ne 0) {
        throw "scp failed for $Voice with exit code $LASTEXITCODE"
    }

    # scp may preserve restrictive local directory modes. The API container only
    # needs read/traverse access, so make the uploaded voice tree publicly readable.
    $remoteVoiceRoot = "$RemoteAudioRoot/$Voice"
    & ssh -o BatchMode=yes -o ConnectTimeout=20 $RemoteHostName "test -d '$remoteVoiceRoot' && find '$remoteVoiceRoot' -type d -exec chmod 755 {} + && find '$remoteVoiceRoot' -type f -name '*.mp3' -exec chmod 644 {} +"
    if ($LASTEXITCODE -ne 0) {
        throw "remote audio permission update failed for $Voice"
    }

    $manifest = Join-Path $logRoot "$Voice.sha256"
    $separator = [IO.Path]::DirectorySeparatorChar
    $voiceMarker = "$separator$Voice$separator"
    $manifestLines = Get-ChildItem -LiteralPath $voiceRoot -Recurse -File -Filter "*.mp3" |
        Sort-Object FullName |
        ForEach-Object {
            $markerIndex = $_.FullName.LastIndexOf($voiceMarker, [StringComparison]::OrdinalIgnoreCase)
            if ($markerIndex -lt 0) {
                throw "Cannot derive relative path for $($_.FullName) under voice $Voice"
            }
            $relativePath = $_.FullName.Substring($markerIndex + $voiceMarker.Length).Replace("\", "/")
            $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$hash  $relativePath"
        }
    Set-Content -LiteralPath $manifest -Value $manifestLines -Encoding ASCII

    $remoteManifest = "/tmp/enplay-$Voice.sha256"
    & scp -o BatchMode=yes -o ConnectTimeout=20 -- $manifest "${RemoteHostName}:${remoteManifest}"
    if ($LASTEXITCODE -ne 0) {
        throw "checksum manifest upload failed for $Voice"
    }
    & ssh -o BatchMode=yes -o ConnectTimeout=20 $RemoteHostName "cd '$RemoteAudioRoot/$Voice' && sha256sum -c '$remoteManifest' >/dev/null && rm -f '$remoteManifest'"
    if ($LASTEXITCODE -ne 0) {
        throw "remote SHA256 verification failed for $Voice"
    }

    Write-BuildStatus "Uploaded and verified $Voice ($($manifestLines.Count) clips)"
}

Write-BuildStatus "Audio build started"
$workers = @(
    if (-not $MaleOnly) {
        Start-AudioWorker -Name "new-sentences-female" -SourceMode "tatoeba" -Voices @("af_heart", "af_bella", "bf_emma")
    }
    Start-AudioWorker -Name "all-content-michael" -SourceMode "all" -Voices @("am_michael")
    Start-AudioWorker -Name "all-content-george" -SourceMode "all" -Voices @("bm_george")
)

$failedWorkers = 0
while (($workers | Where-Object { -not $_.Uploaded }).Count -gt 0) {
    foreach ($worker in $workers | Where-Object { -not $_.Uploaded }) {
        if (-not $worker.Process.HasExited) {
            continue
        }
        $worker.Process.Refresh()
        if ($worker.Process.ExitCode -ne 0) {
            Write-BuildStatus "FAILED $($worker.Name) with exit code $($worker.Process.ExitCode)"
            $worker.Uploaded = $true
            $failedWorkers += 1
            continue
        }
        try {
            foreach ($voice in $worker.Voices) {
                Publish-Voice -Voice $voice
            }
            Write-BuildStatus "Completed $($worker.Name)"
        }
        catch {
            Write-BuildStatus "FAILED publishing $($worker.Name): $($_.Exception.Message)"
            $failedWorkers += 1
        }
        $worker.Uploaded = $true
    }
    if (($workers | Where-Object { -not $_.Uploaded }).Count -gt 0) {
        Start-Sleep -Seconds 15
    }
}

if ($failedWorkers -gt 0) {
    Write-BuildStatus "Audio build finished with $failedWorkers failed worker(s)"
    exit 1
}

Write-BuildStatus "Audio build and verified upload completed successfully"
