#!/bin/bash

# Run the Python script once
python /app/arxiv_download.py >> /app/log/cron.log 2>&1

# Start the cron service
cron

# Keep the container running
tail -f /app/log/cron.log
