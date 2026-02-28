#!/bin/bash
# Automated backup script to be run via cron
# Add to crontab: 0 2 * * * /path/to/cron-backup.sh

set -e

# Load environment variables
if [ -f /app/.env.production ]; then
    export $(cat /app/.env.production | grep -v '^#' | xargs)
fi

# Run backup
/app/scripts/db-backup/backup.sh

# Optional: Upload to cloud storage (uncomment and configure as needed)
# Example for AWS S3:
# aws s3 cp /backup/oscp_backup_$(date +"%Y%m%d")*.sql.gz s3://your-bucket/backups/

# Example for Google Cloud Storage:
# gsutil cp /backup/oscp_backup_$(date +"%Y%m%d")*.sql.gz gs://your-bucket/backups/

# Send notification on failure
if [ $? -ne 0 ]; then
    echo "Backup failed at $(date)" | mail -s "OSCP Backup Failed" admin@example.com
fi
