# 🚀 Deployment Guide

Guide for deploying the Customer Support AI system to production.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] No hardcoded secrets
- [ ] Logging configured
- [ ] Error handling complete
- [ ] Database backups set up
- [ ] Performance tested
- [ ] Security reviewed
- [ ] Documentation updated

## Backend Deployment

### Option 1: Docker (Recommended)

#### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 5000

# Run server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - SARVAM_API_KEY=${SARVAM_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./backend/logs:/app/logs
      - ./backend/policies.json:/app/policies.json
    restart: unless-stopped

  frontend:
    build:
      context: frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### Deploy with Docker

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### Option 2: Heroku

#### 1. Create Procfile

```
web: gunicorn --bind 0.0.0.0:$PORT backend/app:app
```

#### 2. Create runtime.txt

```
python-3.9.13
```

#### 3. Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SARVAM_API_KEY=your_key

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Option 3: AWS EC2

#### 1. Launch EC2 Instance

```bash
# Use Ubuntu 20.04 LTS
# Security group: Allow HTTP (80), HTTPS (443), SSH (22)
```

#### 2. Install Dependencies

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & pip
sudo apt install python3-pip python3-venv -y

# Install Gunicorn & Nginx
pip3 install gunicorn
sudo apt install nginx -y
```

#### 3. Clone & Setup

```bash
git clone <repo-url>
cd cust/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SARVAM_API_KEY=your_key
```

#### 4. Configure Nginx

```nginx
# /etc/nginx/sites-available/default
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

#### 5. Start Services

```bash
# Start Gunicorn
gunicorn --bind 127.0.0.1:5000 --workers 4 app:app &

# Restart Nginx
sudo systemctl restart nginx

# Enable auto-start
sudo systemctl enable nginx
```

#### 6. Setup SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Option 4: Railway.app

#### 1. Connect Repository

```bash
# Push code to GitHub
git push origin main
```

#### 2. Deploy on Railway

- Go to railway.app
- Connect GitHub repository
- Select deployment
- Add environment variables
- Deploy

### Option 5: PythonAnywhere

#### 1. Upload Code

```bash
# Upload via web dashboard or git
git clone <repo> /home/yourname/cust
```

#### 2. Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.9 cust
pip install -r requirements.txt
```

#### 3. Configure Web App

- New web app → Manual configuration → Python 3.9
- WSGI file: Point to app.py
- Virtualenv: Select your venv

#### 4. Set Environment Variables

- Web app settings → Environment variables
- Add: SARVAM_API_KEY=...

## Frontend Deployment

### Option 1: Vercel (Recommended for React)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod

# Configure env vars in Vercel dashboard
REACT_APP_API_URL=https://your-backend.com
```

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod
```

### Option 3: AWS S3 + CloudFront

```bash
# Build React app
cd frontend
npm run build

# Upload to S3
aws s3 sync build/ s3://your-bucket-name

# Setup CloudFront distribution
# Point to S3 bucket
```

### Option 4: Docker (with Nginx)

```dockerfile
# Dockerfile for frontend
FROM node:16 AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Environment Configuration

### Create .env file

```bash
# Backend
SARVAM_API_KEY=your_secret_key
FLASK_ENV=production
FLASK_DEBUG=False

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENV=production
```

### Secure Secrets

```bash
# Option 1: Environment Variables
export SARVAM_API_KEY="key"

# Option 2: .env file (DO NOT commit!)
# Add to .gitignore: .env

# Option 3: Secrets Manager
# AWS Secrets Manager
# Azure Key Vault
# Heroku Config Vars
```

## Database Setup (Optional)

### SQLite (Simple)

```python
# app.py
import sqlite3

DATABASE = 'app.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    return db

# Initialize
@app.before_request
def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY,
            query TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()
```

### PostgreSQL (Production)

```bash
# Install
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb cust_db
sudo -u postgres createuser cust_user
sudo -u postgres psql -c "ALTER ROLE cust_user WITH PASSWORD 'password';"

# Connect in Python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/cust_db'
db = SQLAlchemy(app)
```

## Monitoring & Logging

### Application Monitoring

```python
# app.py with Sentry
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Log Aggregation

```python
# Send logs to external service
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Uptime Monitoring

- Use UptimeRobot or similar
- Monitor `/api/health` endpoint
- Set up alerts

## Performance Optimization

### Caching

```python
# Cache responses
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/modes')
@cache.cached(timeout=3600)
def get_modes():
    # ...
```

### Compression

```python
# Enable gzip compression
from flask_compress import Compress

Compress(app)
```

### CDN Setup

```python
# Use CloudFront/CloudFlare for static assets
# Point to your domain
# Compress assets before upload
```

## Security Hardening

### HTTPS/SSL

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Use in Flask
app.run(ssl_context=('cert.pem', 'key.pem'))
```

### Security Headers

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

@app.route('/api/generate-response', methods=['POST'])
@limiter.limit("20 per minute")
def generate_response():
    # ...
```

### Input Validation

```python
from flask import request
import bleach

@app.route('/api/generate-response', methods=['POST'])
def generate_response():
    data = request.get_json()
    
    # Validate input
    query = data.get('query', '').strip()
    if not query or len(query) > 1000:
        return {'error': 'Invalid query'}, 400
    
    # Sanitize
    query = bleach.clean(query)
    
    # Process...
```

## Backup & Recovery

### Database Backup

```bash
# SQLite
cp app.db app.db.backup

# PostgreSQL
pg_dump cust_db > backup.sql

# Automated (cron)
0 2 * * * pg_dump cust_db > /backups/db_$(date +\%Y\%m\%d).sql
```

### File Backup

```bash
# Backup policies
cp backend/policies.json backend/policies.json.backup

# Backup logs
tar -czf logs_backup.tar.gz backend/logs/
```

## Rollback Strategy

```bash
# Keep multiple versions
git tag v1.0 v1.1 v1.2

# Rollback to previous version
git checkout v1.1
git push -f origin main
docker-compose build && docker-compose up -d
```

## Deployment Checklist

- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] Database migrated
- [ ] Logs configured
- [ ] Backups set up
- [ ] SSL certificate installed
- [ ] Health check endpoint working
- [ ] Monitoring configured
- [ ] Rate limiting enabled
- [ ] Security headers added
- [ ] Load tested
- [ ] Documentation updated
- [ ] Team notified

## Post-Deployment

### Monitor Metrics

```bash
# Check application health
curl https://your-domain.com/api/health

# Monitor performance
# - Response time
# - Error rate
# - CPU usage
# - Memory usage
```

### Set Up Alerts

```bash
# Email alerts for:
# - High error rate
# - API down
# - High memory
# - Disk full
```

### Update DNS

```bash
# Point domain to your server
# Type: A or CNAME
# Value: Your server IP or domain
# TTL: 3600

# Verify
nslookup your-domain.com
```

### Configure Email

```python
# For notifications
from flask_mail import Mail

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)
```

## Continuous Deployment

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: your-app-name
          heroku_email: your-email@example.com
```

## Cost Optimization

### Reduce Expenses

1. **Use Free Tier Services**
   - GitHub (repo hosting)
   - Railway (limited free tier)
   - Vercel (frontend hosting)

2. **Auto-scale Infrastructure**
   - Scale down during off-hours
   - Use spot instances on AWS

3. **Optimize Bandwidth**
   - Enable compression
   - Use CDN
   - Cache aggressively

4. **Database Optimization**
   - Use indexed queries
   - Remove old logs
   - Archive historical data

## Troubleshooting Deployments

### App won't start

```bash
# Check logs
docker logs <container-id>
heroku logs --tail
ssh to server and check journalctl
```

### Port binding issues

```bash
# Use port from environment
port = os.environ.get('PORT', 5000)
app.run(port=port)
```

### Memory limits

```bash
# Monitor memory
# Reduce worker count
# Enable swap
# Use async workers
```

## Rollback Procedure

```bash
# 1. Stop current deployment
docker stop <container>

# 2. Revert code
git revert HEAD

# 3. Redeploy
git push origin main
docker-compose up -d

# 4. Verify
curl https://your-domain.com/api/health
```

---

**Deployment successful! 🎉**

For questions, check README.md or TROUBLESHOOTING.md
