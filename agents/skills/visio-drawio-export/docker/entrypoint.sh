#!/bin/bash
set -e

# Start Xvfb for headless rendering
if [ "$DRAWIO_HEADLESS" = "true" ]; then
    Xvfb :99 -screen 0 1920x1080x24 &
    export DISPLAY=:99
    sleep 1
fi

# Run the export command
exec node /app/src/index.js "$@"
