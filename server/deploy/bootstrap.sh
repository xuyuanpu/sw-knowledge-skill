#!/bin/bash
set -euo pipefail
base=/opt/sw-kb-mcp
id swmcp >/dev/null 2>&1 || useradd --system --home "$base" --shell /sbin/nologin swmcp
mkdir -p "$base/app" "$base/state" "$base/private" "$base/backups"
chmod 700 "$base/private"
chown swmcp:swmcp "$base/state"
chmod 700 "$base/state"
if [ ! -x "$base/python/bin/python3.12" ]; then
  cp -a /opt/hermes/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu "$base/python"
  chown -R root:root "$base/python"
fi
[ -x "$base/venv/bin/python" ] || "$base/python/bin/python3.12" -m venv "$base/venv"
"$base/venv/bin/pip" install --disable-pip-version-check -r "$base/app/requirements.txt" >/opt/sw-kb-mcp/install.log 2>&1
printf 'DEPENDENCIES_READY\n'
