# Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Traditional Server Deployment](#traditional-server-deployment)
- [Cloud Deployment](#cloud-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [SSL/HTTPS Configuration](#sslhttps-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup Strategies](#backup-strategies)
- [Security Considerations](#security-considerations)
- [Scaling and Load Balancing](#scaling-and-load-balancing)
- [Troubleshooting](#troubleshooting)

## Overview

This guide covers deployment options for NextProperty AI in production environments, from containerized deployments to traditional server setups.

### Deployment Options
- **Docker Compose** (Recommended for small-medium deployments)
- **Kubernetes** (For large-scale, enterprise deployments)
- **Traditional Server** (VPS/Dedicated server)
- **Cloud Platforms** (AWS, GCP, Azure, DigitalOcean)

## Environment Setup

### Production Environment Variables

Create a `.env.production` file:

```env
# Application
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
SECURITY_PASSWORD_SALT=your-security-salt-here

# Database
DATABASE_URL=mysql://username:password@db-server:3306/nextproperty_prod
SQLALCHEMY_ENGINE_OPTIONS='{"pool_size": 20, "pool_recycle": 300, "pool_pre_ping": true}'

# Redis Cache
CACHE_TYPE=redis
CACHE_REDIS_HOST=redis-server
CACHE_REDIS_PORT=6379
CACHE_REDIS_DB=0
CACHE_REDIS_PASSWORD=your-redis-password

# External APIs
BOC_API_KEY=your-bank-of-canada-api-key
STATCAN_API_KEY=your-statistics-canada-api-key

# Security
SSL_REQUIRED=True
SESSION_TIMEOUT=3600
BCRYPT_LOG_ROUNDS=12

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/nextproperty/app.log

# Performance
ML_MODELS_PATH=/app/models/trained_models/
PREDICTION_CACHE_TTL=3600
BULK_OPERATION_TIMEOUT=1800

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
NEW_RELIC_LICENSE_KEY=your-newrelic-key-here
```

### Security Environment Variables

```env
# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-256-bits
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# Rate Limiting
RATE_LIMIT_STORAGE_URL=redis://redis-server:6379/1
RATE_LIMIT_DEFAULT=100 per hour

# CORS Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Docker Deployment

### Docker Compose (Recommended)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "80:5007"
      - "443:5007"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://nextproperty:${DB_PASSWORD}@db:3306/nextproperty_prod
      - CACHE_REDIS_HOST=redis
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/var/log/nextproperty
      - ./instance:/app/instance
      - ./models:/app/models
    restart: unless-stopped
    networks:
      - nextproperty-network

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: nextproperty_prod
      MYSQL_USER: nextproperty
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backups:/backups
    ports:
      - "3306:3306"
    restart: unless-stopped
    networks:
      - nextproperty-network
    command: --default-authentication-plugin=mysql_native_password

  redis:
    image: redis:alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - nextproperty-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./static:/var/www/static
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - nextproperty-network

volumes:
  mysql_data:
  redis_data:

networks:
  nextproperty-network:
    driver: bridge
```

### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Create necessary directories
RUN mkdir -p /app/logs /app/instance

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5007/api/health || exit 1

# Expose port
EXPOSE 5007

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5007", "--workers", "4", "--timeout", "120", "app:app"]
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream nextproperty {
        server web:5007;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://nextproperty;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth endpoints with stricter rate limiting
        location ~ /api/(login|register|reset-password) {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://nextproperty;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Main application
        location / {
            proxy_pass http://nextproperty;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Deployment Commands

```bash
# Set environment variables
export MYSQL_ROOT_PASSWORD=your-strong-mysql-root-password
export DB_PASSWORD=your-strong-db-password
export REDIS_PASSWORD=your-strong-redis-password

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Scale web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3

# Update deployment
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup database
docker-compose -f docker-compose.prod.yml exec db mysqldump -u root -p nextproperty_prod > backup_$(date +%Y%m%d).sql
```

## Traditional Server Deployment

### Ubuntu/Debian Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server

# Create application user
sudo useradd -m -s /bin/bash nextproperty
sudo usermod -aG sudo nextproperty

# Create application directory
sudo mkdir -p /opt/nextproperty
sudo chown nextproperty:nextproperty /opt/nextproperty

# Switch to application user
sudo su - nextproperty

# Clone repository
cd /opt/nextproperty
git clone https://github.com/yourusername/nextproperty-ai.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

### Database Setup

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE nextproperty_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nextproperty'@'localhost' IDENTIFIED BY 'strong-password-here';
GRANT ALL PRIVILEGES ON nextproperty_prod.* TO 'nextproperty'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Systemd Service Configuration

Create `/etc/systemd/system/nextproperty.service`:

```ini
[Unit]
Description=NextProperty AI Web Application
After=network.target mysql.service redis.service

[Service]
Type=notify
User=nextproperty
Group=nextproperty
WorkingDirectory=/opt/nextproperty
Environment=PATH=/opt/nextproperty/venv/bin
ExecStart=/opt/nextproperty/venv/bin/gunicorn --bind 127.0.0.1:5007 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nextproperty.service
sudo systemctl start nextproperty.service
sudo systemctl status nextproperty.service
```

### Nginx Configuration (Traditional)

Create `/etc/nginx/sites-available/nextproperty`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5007;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/nextproperty/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nextproperty /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECS Cluster**:
```bash
aws ecs create-cluster --cluster-name nextproperty-cluster
```

2. **Create Task Definition** (`ecs-task-definition.json`):
```json
{
  "family": "nextproperty-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "nextproperty-web",
      "image": "your-ecr-repo/nextproperty:latest",
      "portMappings": [
        {
          "containerPort": 5007,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "mysql://user:pass@rds-endpoint:3306/nextproperty"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextproperty",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Deploy Service**:
```bash
aws ecs create-service \
  --cluster nextproperty-cluster \
  --service-name nextproperty-service \
  --task-definition nextproperty-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Using AWS RDS for Database

```bash
# Create RDS MySQL instance
aws rds create-db-instance \
  --db-instance-identifier nextproperty-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password YourStrongPassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx
```

### DigitalOcean App Platform

Create `app.yaml`:

```yaml
name: nextproperty-ai
services:
- name: web
  source_dir: /
  github:
    repo: your-username/nextproperty-ai
    branch: main
  run_command: gunicorn --bind 0.0.0.0:5007 --workers 4 app:app
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 5007
  envs:
  - key: FLASK_ENV
    value: production
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: CACHE_REDIS_HOST
    value: ${redis.HOSTNAME}
databases:
- engine: MYSQL
  name: nextproperty-db
  num_nodes: 1
  size: db-s-1vcpu-1gb
  version: "8"
- engine: REDIS
  name: nextproperty-redis
  num_nodes: 1
  size: db-s-1vcpu-1gb
```

### Google Cloud Platform (Cloud Run)

1. **Build and push image**:
```bash
# Build image
docker build -t gcr.io/your-project/nextproperty .

# Push to Container Registry
docker push gcr.io/your-project/nextproperty
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy nextproperty \
  --image gcr.io/your-project/nextproperty \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production \
  --memory 2Gi \
  --cpu 2
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app tests/
    
    - name: Lint code
      run: |
        pip install flake8 black
        black --check .
        flake8 .

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.prod
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/nextproperty:latest
    
    - name: Deploy to production
      uses: appleboy/ssh-action@v0.1.7
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USER }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          cd /opt/nextproperty
          docker-compose -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.prod.yml up -d
          docker system prune -f
```

### GitLab CI/CD

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_REGISTRY: registry.gitlab.com
  IMAGE_NAME: $DOCKER_REGISTRY/$CI_PROJECT_PATH

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=app tests/
    - black --check .
    - flake8 .

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -f Dockerfile.prod -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:latest
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  only:
    - main

deploy:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
  script:
    - ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST "
        cd /opt/nextproperty &&
        docker-compose -f docker-compose.prod.yml pull &&
        docker-compose -f docker-compose.prod.yml up -d &&
        docker system prune -f"
  only:
    - main
```

## SSL/HTTPS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Set up auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Manual SSL Certificate

Update nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # SSL session settings
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # ... rest of your configuration
}
```

## Monitoring and Logging

### Application Monitoring

#### Health Check Endpoint

Add to your Flask app:

```python
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Check database connection
        db.session.execute('SELECT 1').scalar()
        
        # Check Redis connection
        from app import cache
        cache.set('health_check', 'ok', timeout=1)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('app_requests_total', 'Total app requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('app_request_duration_seconds', 'Request latency')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.observe(request_latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Centralized Logging

#### ELK Stack Configuration

Create `docker-compose.logging.yml`:

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logs:/logs

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

#### Structured Logging

Update logging configuration:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logger
logger = logging.getLogger('nextproperty')
handler = logging.FileHandler('/var/log/nextproperty/app.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

## Backup Strategies

### Automated Database Backups

Create backup script (`scripts/backup.sh`):

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups"
MYSQL_USER="backup_user"
MYSQL_PASSWORD="backup_password"
DATABASE="nextproperty_prod"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nextproperty_$DATE.sql"

# Create database backup
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD \
  --single-transaction \
  --routines \
  --triggers \
  $DATABASE > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Upload to S3 (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp $BACKUP_FILE.gz s3://$AWS_S3_BUCKET/backups/
fi

# Clean up old backups
find $BACKUP_DIR -name "nextproperty_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

Set up cron job:

```bash
# Edit crontab
crontab -e

# Add backup job (daily at 2 AM)
0 2 * * * /opt/nextproperty/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Application File Backups

```bash
#!/bin/bash
# backup_app.sh

APP_DIR="/opt/nextproperty"
BACKUP_DIR="/backups/app"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='logs' \
  $APP_DIR

# Backup models and instance data
tar -czf $BACKUP_DIR/models_$DATE.tar.gz $APP_DIR/models
tar -czf $BACKUP_DIR/instance_$DATE.tar.gz $APP_DIR/instance

echo "Application backup completed"
```

## Security Considerations

### Security Checklist

- [ ] **Strong passwords** for all accounts
- [ ] **SSL/TLS encryption** for all communications
- [ ] **Firewall rules** restricting access to necessary ports only
- [ ] **Regular security updates** for OS and dependencies
- [ ] **Input validation** and sanitization
- [ ] **Rate limiting** on API endpoints
- [ ] **CORS configuration** for cross-origin requests
- [ ] **Secure headers** (HSTS, CSP, X-Frame-Options)
- [ ] **Database access controls** and least privilege
- [ ] **Log monitoring** for suspicious activities
- [ ] **Backup encryption** for sensitive data
- [ ] **API key rotation** for external services

### Firewall Configuration

```bash
# UFW (Ubuntu Firewall)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Allow specific IP for admin access
sudo ufw allow from YOUR_ADMIN_IP to any port 22
```

### Environment Security

```bash
# Set proper file permissions
chmod 600 .env.production
chmod 600 /etc/ssl/private/your-key.pem
chmod 644 /etc/ssl/certs/your-cert.pem

# Restrict log file access
chmod 640 /var/log/nextproperty/*.log
chown www-data:adm /var/log/nextproperty/*.log
```

## Scaling and Load Balancing

### Horizontal Scaling with Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml nextproperty

# Scale services
docker service scale nextproperty_web=5
```

### Load Balancer Configuration

#### HAProxy Configuration

Create `/etc/haproxy/haproxy.cfg`:

```
global
    daemon
    user haproxy
    group haproxy

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend nextproperty_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/nextproperty.pem
    redirect scheme https if !{ ssl_fc }
    default_backend nextproperty_servers

backend nextproperty_servers
    balance roundrobin
    option httpchk GET /health
    server web1 web1:5007 check
    server web2 web2:5007 check
    server web3 web3:5007 check
```

### Database Scaling

#### Read Replicas

```python
# In config.py for read replica support
SQLALCHEMY_BINDS = {
    'read_replica': 'mysql://user:pass@replica-host:3306/nextproperty_prod'
}

# Usage in models
class Property(db.Model):
    __bind_key__ = None  # Use default (master) for writes
    
    @classmethod
    def get_for_read(cls):
        # Use read replica for read-only queries
        return cls.query.options(db.session.bind_mapper(cls, 'read_replica'))
```

## Troubleshooting

### Common Deployment Issues

#### Container Won't Start

```bash
# Check container logs
docker logs container_name

# Check resource usage
docker stats

# Inspect container
docker inspect container_name

# Check image
docker run -it --rm image_name /bin/bash
```

#### Database Connection Issues

```bash
# Test database connectivity
mysql -h db_host -u username -p database_name

# Check database logs
docker logs mysql_container

# Verify network connectivity
docker exec web_container ping db_container
```

#### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in certificate.crt -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443

# Check certificate expiration
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

#### Performance Issues

```bash
# Monitor resource usage
htop
iotop
nethogs

# Check application metrics
curl http://localhost:5007/metrics

# Database performance
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;
```

### Log Analysis

```bash
# Application errors
grep -i error /var/log/nextproperty/app.log

# Database slow queries
grep "Query_time" /var/log/mysql/slow.log

# Nginx access patterns
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -10
```

For additional troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
