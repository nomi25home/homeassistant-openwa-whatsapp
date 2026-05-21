#!/usr/bin/bash

# Load options from the Home Assistant config file
API_KEY=$(cat /data/options.json | grep -o '"api_master_key":"[^"]*"' | cut -d'"' -f4)

if [ -n "$API_KEY" ]; then
    export API_MASTER_KEY="$API_KEY"
fi

# The image has its own entrypoint, so we should find what it is.
# Based on common OpenWA images, it's likely 'npm start' or 'node index.js'
# But the safest way is to run the original entrypoint.
exec /entrypoint.sh
