# Ubuntu 24.04 native services

These files run the API and on-demand Kokoro audio generation without Docker.
They are deployment assets only: installing them does not enable or start a
service.

The optional `swapfile.swap` unit keeps a pre-created `/swapfile` active after
reboot on small hosts. Create the file with `fallocate`, mode `0600`, and
`mkswap` before installing or enabling that unit. It does not alter
`/etc/fstab`.

## Expected layout

- `/opt/enplay/current` is a root-owned symlink to the active release. The
  release contains `api/`, `generate_recorded_audio.py`, and this directory.
- `/opt/enplay/venv` is a Linux-native Python virtual environment shared by the
  API and audio builder. Install `api/requirements.txt`, then install
  `kokoro-onnx`, `onnxruntime`, `numpy`, `lameenc`, and `soundfile` into it.
- `/opt/enplay/shared/api.env` contains the runtime environment.
- `/opt/enplay/shared/audio` is the live API audio tree.
- `/opt/enplay/shared/audio-build-v1` is staging output for generated clips.
- `/opt/enplay/shared/models` contains `kokoro-v1.0.fp16.onnx` and
  `voices-v1.0.bin`.
- `/opt/enplay/shared/tts-cache` is the only extra writable cache directory for
  the TTS service.

Create a system user such as `enplay` with no login shell. Keep releases, the
virtual environment, service files, and models root-owned and readable by the
`enplay` group. Make only the live/staging audio and TTS cache directories
writable by `enplay`. Recommended modes are `0750` for directories, `0640` for
models and `api.env`, and `0644` for unit files. In particular:

```text
/opt/enplay/current                         root:enplay  0750 (release tree)
/opt/enplay/venv                           root:enplay  0750
/opt/enplay/shared/api.env                 root:enplay  0640
/opt/enplay/shared/models                  root:enplay  0750
/opt/enplay/shared/audio-build-v1          enplay:enplay 0750
/opt/enplay/shared/tts-cache               enplay:enplay 0750
```

`api.env` is sourced as a POSIX shell environment file, so quote values that
contain spaces or shell metacharacters. It must define `ADMIN_TOKEN` and either
`DATABASE_URL` or `MYSQL_PASSWORD`. The wrapper supplies loopback-only native
defaults for MySQL/Redis, derives `PRESENCE_SECRET` from `ADMIN_TOKEN`, uses
`AUDIO_ROOT=/opt/enplay/shared/audio`, and allows both production domain
generations. Any of those defaults can still be overridden in `api.env`. Store
real credentials only in that host-local file, never in the release or unit
files.

## Install without starting

On Ubuntu 24.04, install `python3`, `python3-venv`, and `curl`; add
`openssh-client` only when publishing to another host. The TTS unit uses curl
to wait for the local API health check before generation. A binary `soundfile`
wheel includes libsndfile on Linux; install the `libsndfile1` package when
using a source build.

Create the virtual environment and install both dependency sets:

```sh
sudo python3 -m venv /opt/enplay/venv
sudo /opt/enplay/venv/bin/pip install --requirement /opt/enplay/current/api/requirements.txt
sudo /opt/enplay/venv/bin/pip install kokoro-onnx onnxruntime numpy lameenc soundfile
```

Pin and record the resolved TTS package versions in the production runbook.
Record model checksums after placing the two model assets on the host:

```sh
cd /opt/enplay/shared/models
sha256sum kokoro-v1.0.fp16.onnx voices-v1.0.bin | sudo tee SHA256SUMS >/dev/null
sha256sum --check SHA256SUMS
```

Install and statically verify the units, but do not enable or start them yet:

```sh
sudo install -o root -g root -m 0644 /opt/enplay/current/deploy/systemd/enplay-api.service /etc/systemd/system/
sudo install -o root -g root -m 0644 /opt/enplay/current/deploy/systemd/enplay-tts-generate@.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemd-analyze verify /etc/systemd/system/enplay-api.service /etc/systemd/system/enplay-tts-generate@.service
```

The API wrapper always binds Uvicorn to `127.0.0.1:28100`; expose it only
through a local reverse proxy. When an operator explicitly starts a TTS unit,
the API is brought up as its dependency so the generator can collect protected
wordbook and sentence data from `http://127.0.0.1:28100`.

The TTS template instance is one voice ID. Its default source mode is `all`:

```sh
sudo systemctl start enplay-tts-generate@am_michael.service
journalctl --unit enplay-tts-generate@am_michael.service --follow
```

Do not start several instances on a 4-core/4-GB host. The unit is capped at two
CPU cores, runs at nice level 10, and has a 2500 MB memory ceiling. To retain
the repository's existing female-voice behavior, create a host-local file such
as `/opt/enplay/shared/tts-af_heart.env` containing only:

```text
TTS_SOURCE_MODE=tatoeba
```

Use the same override for `af_bella` and `bf_emma`; male voices normally keep
the `all` default. These override files contain no credentials and should be
owned by `root:enplay` with mode `0640`.

## Verification and promotion

After manually starting the API, confirm that it is healthy and bound only to
loopback:

```sh
curl --fail --silent --show-error http://127.0.0.1:28100/health
ss --tcp --listen --numeric --process | grep '127.0.0.1:28100'
```

After a TTS job succeeds, an empty-file check must print nothing. Generate and
verify a deterministic manifest before promoting the staging tree:

```sh
find /opt/enplay/shared/audio-build-v1 -type f -name '*.mp3' -empty -print
cd /opt/enplay/shared/audio-build-v1/v1
find . -type f -name '*.mp3' -print0 | sort -z | xargs -0 sha256sum >../audio-build-v1.sha256
sha256sum --check ../audio-build-v1.sha256
```

Keep the previous live audio tree until the new manifest has passed. Promotion
is intentionally not automated by these units.
