#!/bin/bash

printenv > /etc/environment
(echo "$INTERVAL /app/run.sh") | crontab -
cron -f
