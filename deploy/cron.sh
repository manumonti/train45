#!/bin/bash

printenv > /etc/environment
(echo "$INTERVAL /app/deploy/run.sh") | crontab -
cron -f
