#!/bin/bash

set -e
touch /root/.cache/log/cron.log
printenv | crontab -
(crontab -l; echo "$INTERVAL /app/deploy/run.sh >> /root/.cache/log/cron.log 2>&1") | crontab -
echo "Setup cron timecode: $INTERVAL"
cron -f
