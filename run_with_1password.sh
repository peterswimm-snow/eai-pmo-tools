#!/usr/bin/env sh
set -eu

# Requirement for this repo (mirrors ../Enterprise_RTB/run_with_1password.sh):
# any tool here that needs a credential resolves it from 1Password via an
# op:// reference in .env, never as a plaintext value. Run tools through
# this wrapper so those references become real env vars before the command
# starts. See .env.1password.example for why devx-cli's own auth is the one
# exception that doesn't go through this path.

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ENV_FILE=${OP_ENV_FILE:-"$SCRIPT_DIR/.env"}

if ! command -v op >/dev/null 2>&1; then
    echo "1Password CLI not found. Install it from https://developer.1password.com/docs/cli/get-started/" >&2
    exit 127
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "No $ENV_FILE found. Copy .env.1password.example to .env (with real op:// references) first." >&2
    echo "If no secrets are needed yet, run the command directly instead of through this wrapper." >&2
    exit 1
fi

exec op run --env-file "$ENV_FILE" -- "$@"
