# Deploying Contributors.in on AWS

Complete step-by-step guide to deploy the full platform on AWS with your `contributors.in` domain from GoDaddy. Database stays on Supabase.

---

## Architecture Overview

```
                    contributors.in (GoDaddy DNS → AWS)
                              │
                              ▼
                    ┌─────────────────┐
                    │  AWS CloudFront  │  (CDN + SSL)
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
   ┌─────────────────┐          ┌─────────────────┐
   │  EC2 Instance    │          │  EC2 Instance    │
   │  (Frontend)      │          │  (Backend)       │
   │  Next.js :3000   │          │  FastAPI :8000   │
   └─────────────────┘          └─────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │    Supabase      │
                               │   (PostgreSQL)   │
                               └─────────────────┘
```

What goes where:
- **Supabase** — PostgreSQL database (already set up)
- **AWS EC2** — Two instances: one for frontend (Next.js), one for backend (FastAPI)
- **AWS CloudFront** — CDN + free SSL certificate
- **GoDaddy** — DNS pointing to AWS

---

## Prerequisites

- AWS account (free tier works for starting out)
- Supabase project with database (already done per your setup)
- GoDaddy account with `contributors.in` domain
- Your local project working and tested
- GitHub OAuth app configured

---

## Step 1: Set Up AWS Account & CLI

### 1.1 Create an AWS Account
If you don't have one: https://aws.amazon.com/free

### 1.2 Install AWS CLI on your Mac

```bash
brew install awscli
```

### 1.3 Configure AWS CLI

Go to AWS Console → IAM → Users → Create a user with `AdministratorAccess` policy.
Create an access key for CLI use.

```bash
aws configure
```

Enter:
- Access Key ID: (from IAM)
- Secret Access Key: (from IAM)
- Default region: `ap-south-1` (Mumbai, closest to India) or `us-east-1`
- Output format: `json`

---

## Step 2: Create a Key Pair for SSH

You need this to SSH into your EC2 instances.

```bash
aws ec2 create-key-pair \
  --key-name contributors-in-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/contributors-in-key.pem

chmod 400 ~/.ssh/contributors-in-key.pem
```

---

## Step 3: Create a Security Group

This controls what traffic can reach your servers.

```bash
# Create the security group
aws ec2 create-security-group \
  --group-name contributors-in-sg \
  --description "Security group for contributors.in"
```

Note the `GroupId` from the output (e.g., `sg-0abc123...`).

```bash
# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress \
  --group-name contributors-in-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
  --group-name contributors-in-sg \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# Allow HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
  --group-name contributors-in-sg \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Allow Next.js (port 3000)
aws ec2 authorize-security-group-ingress \
  --group-name contributors-in-sg \
  --protocol tcp --port 3000 --cidr 0.0.0.0/0

# Allow FastAPI (port 8000)
aws ec2 authorize-security-group-ingress \
  --group-name contributors-in-sg \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0
```

---

## Step 4: Launch EC2 Instances

We'll use two `t3.small` instances (2 vCPU, 2GB RAM — good enough to start, ~$15/month each).

### 4.1 Find the latest Ubuntu AMI

```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text
```

Note the AMI ID (e.g., `ami-0abc123...`).

### 4.2 Launch Backend Instance

```bash
aws ec2 run-instances \
  --image-id <AMI_ID> \
  --instance-type t3.small \
  --key-name contributors-in-key \
  --security-groups contributors-in-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=contributors-in-backend}]' \
  --count 1
```

### 4.3 Launch Frontend Instance

```bash
aws ec2 run-instances \
  --image-id <AMI_ID> \
  --instance-type t3.small \
  --key-name contributors-in-key \
  --security-groups contributors-in-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=contributors-in-frontend}]' \
  --count 1
```

### 4.4 Allocate Elastic IPs (so IPs don't change on restart)

```bash
# For backend
aws ec2 allocate-address --domain vpc
# Note the AllocationId and PublicIp

# For frontend
aws ec2 allocate-address --domain vpc
# Note the AllocationId and PublicIp
```

Associate them:

```bash
# Get instance IDs
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=contributors-in-backend" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text

aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=contributors-in-frontend" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text

# Associate Elastic IPs
aws ec2 associate-address --instance-id <BACKEND_INSTANCE_ID> --allocation-id <BACKEND_ALLOC_ID>
aws ec2 associate-address --instance-id <FRONTEND_INSTANCE_ID> --allocation-id <FRONTEND_ALLOC_ID>
```

---

## Step 5: Set Up the Backend Server

### 5.1 SSH into the backend instance

```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<BACKEND_ELASTIC_IP>
```

### 5.2 Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx
```

### 5.3 Clone your repo

```bash
cd /home/ubuntu
git clone <YOUR_REPO_URL> app
cd app/backend
```

### 5.4 Set up Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5.5 Create the .env file

```bash
nano .env
```

Paste your production config:

```env
# Database — your Supabase connection string
DATABASE_URL=postgresql://postgres.xxxx:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Security — generate a new one for production
SECRET_KEY=<run: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub OAuth
GITHUB_CLIENT_ID=your_production_github_client_id
GITHUB_CLIENT_SECRET=your_production_github_client_secret
GITHUB_TOKEN=ghp_your_token_for_issue_sync

# AWS Bedrock (for AI features)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# CORS — allow your domain
CORS_ORIGINS=["https://contributors.in","https://www.contributors.in"]

# Environment
ENVIRONMENT=production
```

### 5.6 Run database migrations

```bash
source venv/bin/activate
alembic upgrade head
```

### 5.7 Seed repositories (optional, do this once)

```bash
python seed_repos.py
```

### 5.8 Create a systemd service for the backend

```bash
sudo nano /etc/systemd/system/contributors-backend.service
```

Paste:

```ini
[Unit]
Description=Contributors.in Backend API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app/backend
Environment="PATH=/home/ubuntu/app/backend/venv/bin"
ExecStart=/home/ubuntu/app/backend/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile /var/log/contributors-backend-access.log \
  --error-logfile /var/log/contributors-backend-error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable contributors-backend
sudo systemctl start contributors-backend
sudo systemctl status contributors-backend
```

### 5.9 Set up Nginx reverse proxy for backend

```bash
sudo nano /etc/nginx/sites-available/contributors-backend
```

Paste:

```nginx
server {
    listen 80;
    server_name api.contributors.in;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/contributors-backend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 6: Set Up the Frontend Server

### 6.1 SSH into the frontend instance

```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<FRONTEND_ELASTIC_IP>
```

### 6.2 Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git nginx certbot python3-certbot-nginx

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 6.3 Clone your repo

```bash
cd /home/ubuntu
git clone <YOUR_REPO_URL> app
cd app/frontend
```

### 6.4 Create the .env.local file

```bash
nano .env.local
```

Paste:

```env
# Points to your backend API
NEXT_PUBLIC_API_URL=https://api.contributors.in

# GitHub OAuth (same app, but update callback URL for production)
GITHUB_CLIENT_ID=your_production_github_client_id
GITHUB_CLIENT_SECRET=your_production_github_client_secret

# NextAuth — generate a new one
AUTH_SECRET=<run: openssl rand -base64 32>

# Production
NODE_ENV=production
NEXTAUTH_URL=https://contributors.in
```

### 6.5 Build the frontend

```bash
npm install
npm run build
```

### 6.6 Install PM2 (process manager for Node.js)

```bash
sudo npm install -g pm2
```

### 6.7 Start the frontend with PM2

```bash
pm2 start npm --name "contributors-frontend" -- start
pm2 save
pm2 startup
```

Run the command PM2 outputs (it will look like `sudo env PATH=... pm2 startup ...`).

### 6.8 Set up Nginx reverse proxy for frontend

```bash
sudo nano /etc/nginx/sites-available/contributors-frontend
```

Paste:

```nginx
server {
    listen 80;
    server_name contributors.in www.contributors.in;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/contributors-frontend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 7: Point Your Domain (GoDaddy DNS)

### 7.1 Log into GoDaddy → My Domains → contributors.in → DNS Management

### 7.2 Add/Edit these DNS records:

| Type  | Name  | Value                    | TTL    |
|-------|-------|--------------------------|--------|
| A     | @     | `<FRONTEND_ELASTIC_IP>`  | 600    |
| A     | www   | `<FRONTEND_ELASTIC_IP>`  | 600    |
| A     | api   | `<BACKEND_ELASTIC_IP>`   | 600    |

- `@` = root domain (`contributors.in`)
- `www` = `www.contributors.in`
- `api` = `api.contributors.in` (your backend)

### 7.3 Wait for DNS propagation (usually 5–30 minutes)

Check with:
```bash
dig contributors.in
dig api.contributors.in
```

---

## Step 8: Set Up SSL (Free with Let's Encrypt)

### 8.1 On the Backend server

```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<BACKEND_ELASTIC_IP>

sudo certbot --nginx -d api.contributors.in
```

Follow the prompts. Certbot will automatically configure Nginx for HTTPS.

### 8.2 On the Frontend server

```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<FRONTEND_ELASTIC_IP>

sudo certbot --nginx -d contributors.in -d www.contributors.in
```

### 8.3 Auto-renewal (already set up by certbot, but verify)

```bash
sudo certbot renew --dry-run
```

---

## Step 9: Update GitHub OAuth App for Production

Go to https://github.com/settings/developers → your OAuth app.

Update:
- **Homepage URL:** `https://contributors.in`
- **Authorization callback URL:** `https://contributors.in/api/auth/callback/github`

---

## Step 10: Verify Everything Works

### 10.1 Check backend health
```bash
curl https://api.contributors.in/health
# Should return: {"status":"healthy"}
```

### 10.2 Check API docs
Open: `https://api.contributors.in/docs`

### 10.3 Check frontend
Open: `https://contributors.in`

### 10.4 Test GitHub login
Click "Sign In" → should redirect to GitHub → back to dashboard.

---

## Ongoing Maintenance

### Deploying updates

On the backend server:
```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<BACKEND_ELASTIC_IP>
cd /home/ubuntu/app
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart contributors-backend
```

On the frontend server:
```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<FRONTEND_ELASTIC_IP>
cd /home/ubuntu/app
git pull
cd frontend
npm install
npm run build
pm2 restart contributors-frontend
```

### Viewing logs

```bash
# Backend
sudo journalctl -u contributors-backend -f
cat /var/log/contributors-backend-error.log

# Frontend
pm2 logs contributors-frontend
```

### Syncing new issues (run periodically)

```bash
ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<BACKEND_ELASTIC_IP>
cd /home/ubuntu/app/backend
source venv/bin/activate
python seed_repos.py --sync-only
```

Or set up a cron job:
```bash
crontab -e
```
Add (runs every 6 hours):
```
0 */6 * * * cd /home/ubuntu/app/backend && /home/ubuntu/app/backend/venv/bin/python seed_repos.py --sync-only >> /var/log/issue-sync.log 2>&1
```

---

## Cost Estimate (Monthly)

| Service              | Cost          |
|----------------------|---------------|
| EC2 t3.small × 2    | ~$30          |
| Elastic IPs × 2     | Free (if attached to running instances) |
| Supabase (free tier) | $0            |
| Let's Encrypt SSL   | $0            |
| GoDaddy domain      | Already purchased |
| **Total**            | **~$30/month** |

If you want to reduce costs, you can run both frontend and backend on a single `t3.small` instance (~$15/month) by running both services on different ports behind Nginx.

---

## Single-Instance Setup (Budget Option)

If you want to save money, run everything on one EC2 instance:

1. Launch one `t3.small` (or even `t3.micro` for free tier)
2. Install both Python and Node.js on it
3. Run backend on port 8000, frontend on port 3000
4. Configure Nginx to route:
   - `contributors.in` → `localhost:3000`
   - `api.contributors.in` → `localhost:8000`
5. Get SSL for both domains on the same server

The Nginx config for single instance:

```nginx
# Frontend
server {
    listen 80;
    server_name contributors.in www.contributors.in;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}

# Backend API
server {
    listen 80;
    server_name api.contributors.in;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Then run certbot for both:
```bash
sudo certbot --nginx -d contributors.in -d www.contributors.in -d api.contributors.in
```

---

## Troubleshooting

**Can't SSH into instance:**
- Check security group allows port 22
- Check you're using the right key: `ssh -i ~/.ssh/contributors-in-key.pem ubuntu@<IP>`

**Backend won't start:**
- Check logs: `sudo journalctl -u contributors-backend -n 50`
- Check .env has correct DATABASE_URL
- Test manually: `cd /home/ubuntu/app/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Frontend build fails:**
- Check Node.js version: `node --version` (need 18+)
- Check .env.local has correct NEXT_PUBLIC_API_URL
- Try: `rm -rf .next node_modules && npm install && npm run build`

**SSL certificate fails:**
- Make sure DNS is pointing to the right IP: `dig contributors.in`
- Make sure port 80 is open in security group
- Make sure Nginx is running: `sudo systemctl status nginx`

**GitHub OAuth not working after deploy:**
- Update callback URL in GitHub OAuth app to `https://contributors.in/api/auth/callback/github`
- Make sure GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET match in both frontend and backend .env files

**Database connection fails:**
- Check Supabase is not restricting your EC2 IP
- Use port 6543 (pooler), not 5432
- Test from EC2: `curl -s telnet://aws-0-us-east-1.pooler.supabase.com:6543`
