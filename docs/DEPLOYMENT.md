# Deployment Guide

This guide covers deploying the Open Source Contribution Platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured with DNS pointing to your server
- Minimum 4GB RAM, 2 CPU cores, 20GB disk space
- PostgreSQL 15+, Redis 7+
- GitHub OAuth application credentials
- OpenAI API key

## Environment Configuration

### 1. Create Production Environment File

```bash
cp .env.production.example .env.production
```

### 2. Configure Required Variables

Edit `.env.production` and set the following:

**Database:**
```bash
POSTGRES_DB=oscp_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
```

**Redis:**
```bash
REDIS_PASSWORD=<strong-password>
```

**Application Security:**
```bash
SECRET_KEY=<generate-with: openssl rand -hex 32>
NEXTAUTH_SECRET=<generate-with: openssl rand -hex 32>
```

**GitHub OAuth:**
```bash
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
```

**OpenAI:**
```bash
OPENAI_API_KEY=<your-openai-api-key>
```

**URLs:**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXTAUTH_URL=https://yourdomain.com
```

### 3. Configure Optional Services

**Monitoring (Sentry):**
```bash
SENTRY_DSN=<your-sentry-dsn>
```

**Email Notifications:**
```bash
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=<email-password>
SMTP_FROM=noreply@yourdomain.com
```

## Database Setup

### Initial Setup

The database will be automatically initialized on first deployment. Migrations are run automatically.

### Manual Migration

If you need to run migrations manually:

```bash
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### Check Migration Status

```bash
docker-compose -f docker-compose.prod.yml run --rm backend alembic current
```

### Create New Migration

```bash
docker-compose -f docker-compose.prod.yml run --rm backend alembic revision --autogenerate -m "Description"
```

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended for Production)

1. Install Certbot:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. Generate certificate:
```bash
sudo certbot certonly --webroot -w /var/www/certbot -d yourdomain.com -d www.yourdomain.com
```

3. Copy certificates:
```bash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

4. Set up auto-renewal:
```bash
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

### Option 2: Self-Signed Certificate (Development/Testing)

```bash
./scripts/generate-ssl-cert.sh
```

## Deployment

### First-Time Deployment

1. **Clone the repository:**
```bash
git clone <repository-url>
cd open-source-contribution-platform
```

2. **Configure environment:**
```bash
cp .env.production.example .env.production
# Edit .env.production with your values
```

3. **Generate SSL certificates:**
```bash
./scripts/generate-ssl-cert.sh
# Or use Let's Encrypt for production
```

4. **Make scripts executable:**
```bash
chmod +x scripts/*.sh
chmod +x scripts/db-backup/*.sh
```

5. **Deploy:**
```bash
./scripts/deploy.sh
```

### Updating Deployment

```bash
git pull origin main
./scripts/deploy.sh
```

### Rollback

If something goes wrong:

```bash
./scripts/rollback.sh
```

## Monitoring

### Access Monitoring Tools

- **Grafana:** http://your-server:3001
  - Default credentials: admin / (set in .env.production)
  - Configure dashboards for application metrics

- **Prometheus:** http://your-server:9090
  - View raw metrics and alerts

### Health Checks

```bash
# Run health check script
./scripts/health-check.sh

# Or check individual endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/detailed
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Metrics

Application metrics are exposed at:
- Backend: http://localhost:8000/metrics
- Prometheus: http://localhost:9090

Key metrics to monitor:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `db_pool_connections_in_use` - Database connection usage
- `celery_queue_length` - Background task queue size
- `issues_claimed_total` - Business metric: issues claimed
- `prs_merged_total` - Business metric: PRs merged

## Backup and Recovery

### Automated Backups

Set up automated daily backups:

```bash
# Add to crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /path/to/scripts/db-backup/cron-backup.sh
```

### Manual Backup

```bash
docker-compose -f docker-compose.prod.yml exec postgres \
  /backup/backup.sh
```

### Restore from Backup

```bash
# List available backups
ls -lh scripts/db-backup/

# Restore specific backup
docker-compose -f docker-compose.prod.yml exec postgres \
  /backup/restore.sh /backup/oscp_backup_20240101_020000.sql.gz
```

### Backup to Cloud Storage

Edit `scripts/db-backup/cron-backup.sh` and uncomment the cloud storage section:

**AWS S3:**
```bash
aws s3 cp /backup/oscp_backup_*.sql.gz s3://your-bucket/backups/
```

**Google Cloud Storage:**
```bash
gsutil cp /backup/oscp_backup_*.sql.gz gs://your-bucket/backups/
```

## Security Best Practices

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. Regular Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
./scripts/deploy.sh
```

### 3. Secrets Management

- Never commit `.env.production` to version control
- Use environment variables or secrets management tools
- Rotate secrets regularly
- Use strong, unique passwords

### 4. Database Security

- Use strong passwords
- Restrict database access to application only
- Enable SSL for database connections
- Regular backups

### 5. Monitoring and Alerts

- Set up Sentry for error tracking
- Configure Prometheus alerts
- Monitor logs for suspicious activity
- Set up uptime monitoring

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Database Connection Issues

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d oscp_db -c "SELECT 1"
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services to free memory
docker-compose -f docker-compose.prod.yml restart
```

### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Regenerate self-signed certificate
./scripts/generate-ssl-cert.sh

# Or renew Let's Encrypt certificate
sudo certbot renew
```

### Performance Issues

1. Check metrics in Grafana
2. Review slow query logs
3. Check Redis cache hit rate
4. Monitor Celery queue length
5. Review application logs for errors

### Emergency Procedures

**Service Down:**
```bash
./scripts/health-check.sh
docker-compose -f docker-compose.prod.yml restart
```

**Database Corruption:**
```bash
./scripts/db-backup/restore.sh /backup/latest_backup.sql.gz
```

**Complete System Failure:**
```bash
./scripts/rollback.sh
```

## Maintenance

### Scheduled Maintenance

1. Announce maintenance window to users
2. Enable maintenance mode:
```bash
# Set in .env.production
MAINTENANCE_MODE=true
```
3. Restart services:
```bash
docker-compose -f docker-compose.prod.yml restart
```
4. Perform maintenance tasks
5. Disable maintenance mode and restart

### Database Maintenance

```bash
# Vacuum database
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d oscp_db -c "VACUUM ANALYZE"

# Check database size
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d oscp_db -c "SELECT pg_size_pretty(pg_database_size('oscp_db'))"
```

### Log Rotation

Logs are automatically rotated by Docker and the application. To manually clean old logs:

```bash
# Clean Docker logs
docker system prune -a --volumes

# Clean application logs
find backend/logs -name "*.log" -mtime +30 -delete
```

## Support

For issues and questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Run health check: `./scripts/health-check.sh`
- Review metrics in Grafana
- Check GitHub issues for known problems
