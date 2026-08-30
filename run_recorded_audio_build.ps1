param(
    [Parameter(Mandatory = $true)]
    [string]$Workspace,
    [Parameter(Mandatory = $true)]
    [string]$BuildRoot,
    [string]$RemoteHostName = "aoke@192.168.0.103",
    [string]$RemoteAudioRoot = "/home/aoke/apps/cet4-study/audio/v1"
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

    $stdout = Join-Path $logRoot "$Name.stdout.log"
    $stderr = Join-Path $logRoot "$Name.stderr.log"
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
        -ArgumentList $arguments `
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
    & scp -r -- $voiceRoot "${RemoteHostName}:${RemoteAudioRoot}/"
    if ($LASTEXITCODE -ne 0) {
        throw "scp failed for $Voice with exit code $LASTEXITCODE"
    }

    $manifest = Join-Path $logRoot "$Voice.sha256"
    $voicePrefixLength = $voiceRoot.Length + 1
    $manifestLines = Get-ChildItem -LiteralPath $voiceRoot -Recurse -File -Filter "*.mp3" |
        Sort-Object FullName |
        ForEach-Object {
            $relativePath = $_.FullName.Substring($voicePrefixLength).Replace("\", "/")
            $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$hash  $relativePath"
        }
    Set-Content -LiteralPath $manifest -Value $manifestLines -Encoding ASCII

    $remoteManifest = "/tmp/enplay-$Voice.sha256"
    & scp -- $manifest "${RemoteHostName}:${remoteManifest}"
    if ($LASTEXITCODE -ne 0) {
        throw "checksum manifest upload failed for $Voice"
    }
    & ssh $RemoteHostName "cd '$RemoteAudioRoot/$Voice' && sha256sum -c '$remoteManifest' >/dev/null && rm -f '$remoteManifest'"
    if ($LASTEXITCODE -ne 0) {
        throw "remote SHA256 verification failed for $Voice"
    }

    Write-BuildStatus "Uploaded and verified $Voice ($($manifestLines.Count) clips)"
}

Write-BuildStatus "Audio build started"
$workers = @(
    Start-AudioWorker -Name "new-sentences-female" -SourceMode "tatoeba" -Voices @("af_heart", "af_bella", "bf_emma")
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
