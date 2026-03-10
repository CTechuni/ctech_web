# Production Deployment Guide - CTech Backend

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration
```bash
# Copy y configurar el archivo .env
cp .env.example .env
nano .env  # Editar con valores de producción
```

**Valores críticos a actualizar:**
- `ENVIRONMENT=production`
- `DEBUG=False`
- `JWT_SECRET_KEY=<strong-random-key>`
- `ADMIN_PASSWORD=<strong-password>`
- `ALLOWED_ORIGINS=<your-domain>`
- Todas las credenciales de BD y Cloudinary

### 2. Generar JWT Secret Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. Verificación de Dependencias
```bash
# Activar virtual environment
source backend/.venv/bin/activate  # Linux/Mac
# o
backend\.venv\Scripts\Activate.ps1  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Agregar Gunicorn para producción
pip install gunicorn
```

---

## 🗄️ Database Setup

### 1. PostgreSQL Configuration
```sql
-- Crear base de datos
CREATE DATABASE ctech_db;

-- Crear usuario con permisos limitados
CREATE USER ctech_user WITH PASSWORD 'strong_password_here';

-- Dar permisos
GRANT CONNECT ON DATABASE ctech_db TO ctech_user;
GRANT USAGE ON SCHEMA public TO ctech_user;
GRANT CREATE ON SCHEMA public TO ctech_user;
\c ctech_db
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ctech_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ctech_user;
```

### 2. Database Initialization
```bash
python -c "from app.core.database import init_db; init_db()"
```

---

## 🚀 Local Testing (Before Deployment)

### 1. Install All Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests (if available)
```bash
pytest tests/ -v
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Endpoints
```bash
curl http://localhost:8000/health
```

---

## 🌐 Production Deployment

### Option 1: Traditional Server (Linux)

#### 1.1 Install Gunicorn & Dependencies
```bash
pip install gunicorn uvicorn
```

#### 1.2 Create Systemd Service File
```bash
sudo nano /etc/systemd/system/ctech-api.service
```

```ini
[Unit]
Description=CTech API Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/CTech/backend
Environment="PATH=/path/to/CTech/backend/.venv/bin"
EnvironmentFile=/path/to/CTech/backend/.env
ExecStart=/path/to/CTech/backend/.venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/log/ctech/access.log \
    --error-logfile /var/log/ctech/error.log \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 1.3 Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start ctech-api
sudo systemctl enable ctech-api
```

#### 1.4 Configure Nginx
```nginx
upstream ctech_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    location / {
        proxy_pass http://ctech_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://ctech_api;
    }
}
```

#### 1.5 Enable HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

---

### Option 2: Vercel/Serverless Deployment

#### 2.1 Create vercel.json
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "env": {
    "PYTHONUNBUFFERED": "1"
  },
  "functions": {
    "app/main.py": {
      "memory": 512,
      "maxDuration": 30
    }
  }
}
```

#### 2.2 Update Database Configuration
```python
# app/core/database.py - Vercel compatibility
from sqlalchemy.pool import NullPool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,  # No connection pooling for serverless
    connect_args={"sslmode": "require"}
)
```

#### 2.3 Deploy
```bash
npm i -g vercel
vercel --prod
```

---

### Option 3: Docker Deployment

#### 3.1 Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]
```

#### 3.2 Create docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:
```

#### 3.3 Run Docker
```bash
docker-compose up -d
```

---

## 📊 Monitoring & Maintenance

### 1. Log Management
```bash
# View logs
tail -f logs/app.log

# Rotate logs
logrotate -f /etc/logrotate.d/ctech-api
```

### 2. Health Monitoring
```bash
# Check service status
curl https://api.yourdomain.com/health

# Monitor with Uptime Robot or similar
# Set webhook to: https://api.yourdomain.com/health
```

### 3. Database Backups
```bash
# Daily backup
0 2 * * * pg_dump -U ${DB_USER} -h ${DB_HOST} ${DB_NAME} | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# S3 backup
aws s3 cp /backups/db-*.sql.gz s3://your-backup-bucket/
```

### 4. Update & Maintenance
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart ctech-api
```

---

## 🔐 Security Hardening

### 1. Firewall Rules
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL/TLS Configuration
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

### 3. Environment Secrets
```bash
# Use environment-specific keys
chmod 600 .env
chmod 600 .env.production

# Store secrets in secret manager (AWS Secrets Manager, HashiCorp Vault, etc.)
```

---

## 🐛 Troubleshooting

### Issue: Database Connection Timeout
```bash
# Check PostgreSQL connection
psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1"

# Check firewall
nc -zv ${DB_HOST} 5432
```

### Issue: API Not Responding
```bash
# Check service status
sudo systemctl status ctech-api

# View error logs
tail -50 /var/log/ctech/error.log

# Restart service
sudo systemctl restart ctech-api
```

### Issue: High Memory Usage
```bash
# Reduce worker count (in systemd service)
# ExecStart=/path/to/.venv/bin/gunicorn --workers 2 ...

# Check for memory leaks
ps aux | grep gunicorn
```

---

## 📞 Support & Escalation

For production issues:
1. Check logs: `tail -f logs/app.log`
2. Verify health: `curl /health`
3. Check database connection
4. Review recent deployments
5. Escalate to DevOps team
