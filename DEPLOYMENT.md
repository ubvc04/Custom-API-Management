# Production Deployment Guide

This guide covers deploying the API Manager application to various production environments.

## Prerequisites

- Git repository with your code
- Environment variables configured
- Database setup (SQLite for development, PostgreSQL recommended for production)

## Environment Variables

Before deploying, ensure you have these environment variables set:

```env
SECRET_KEY=your-super-secret-production-key
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
DATABASE_URL=sqlite:///api_manager.db
```

## Deployment Options

### 1. Render.com (Recommended)

Render provides easy deployment with automatic HTTPS and custom domains.

#### Setup Steps:

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `api-manager`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --config gunicorn_config.py app:app`

3. **Set Environment Variables**
   ```
   SECRET_KEY=your-production-secret-key
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Deployment will start automatically

#### Custom Domain (Optional):
- Go to Settings → Custom Domains
- Add your domain and configure DNS

### 2. Railway.app

Railway offers simple deployment with automatic scaling.

#### Setup Steps:

1. **Deploy from GitHub**
   - Go to [Railway](https://railway.app/)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"

2. **Configure Variables**
   - Go to Variables tab
   - Add all required environment variables

3. **Custom Start Command**
   - Add start command: `gunicorn --config gunicorn_config.py app:app`

### 3. Heroku

Traditional platform with extensive add-on ecosystem.

#### Setup Steps:

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Configure Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set SMTP_USERNAME=your-email@gmail.com
   heroku config:set SMTP_PASSWORD=your-app-password
   ```

4. **Create Procfile**
   ```bash
   echo "web: gunicorn --config gunicorn_config.py app:app" > Procfile
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### 4. DigitalOcean App Platform

#### Setup Steps:

1. **Create App**
   - Go to DigitalOcean Control Panel
   - Apps → Create App
   - Connect GitHub repository

2. **Configure Build**
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn --config gunicorn_config.py app:app`

3. **Set Environment Variables**
   - Add all required environment variables in App settings

### 5. AWS Elastic Beanstalk

#### Setup Steps:

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Application**
   ```bash
   eb init -p python-3.11 api-manager
   ```

3. **Create Environment**
   ```bash
   eb create api-manager-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv SECRET_KEY=your-secret-key SMTP_USERNAME=your-email@gmail.com
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and Run**
   ```bash
   docker-compose up -d
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop Services**
   ```bash
   docker-compose down
   ```

### Manual Docker Deployment

1. **Build Image**
   ```bash
   docker build -t api-manager .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name api-manager \
     -p 8000:8000 \
     -e SECRET_KEY=your-secret-key \
     -e SMTP_USERNAME=your-email@gmail.com \
     -e SMTP_PASSWORD=your-app-password \
     api-manager
   ```

## VPS/Server Deployment

### Ubuntu/Debian Server

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Dependencies**
   ```bash
   sudo apt install python3 python3-pip python3-venv nginx git -y
   ```

3. **Clone Repository**
   ```bash
   git clone <your-repo-url> /var/www/api-manager
   cd /var/www/api-manager
   ```

4. **Setup Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

6. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/api-manager.service
   ```

   ```ini
   [Unit]
   Description=API Manager
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/api-manager
   Environment=PATH=/var/www/api-manager/venv/bin
   ExecStart=/var/www/api-manager/venv/bin/gunicorn --config gunicorn_config.py app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start api-manager
   sudo systemctl enable api-manager
   ```

8. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/api-manager
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/api-manager /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Setup SSL (Optional)**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

## Database Migration to PostgreSQL

For production, consider migrating from SQLite to PostgreSQL:

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
```

**Docker:**
```bash
docker run --name postgres-db -e POSTGRES_PASSWORD=password -d postgres
```

### 2. Update Requirements
Add to `requirements.txt`:
```
psycopg2-binary==2.9.7
```

### 3. Update Environment Variables
```env
DATABASE_URL=postgresql://username:password@localhost/api_manager
```

### 4. Data Migration
```python
# Create migration script
import sqlite3
import psycopg2
# Add migration logic here
```

## Monitoring and Logging

### 1. Application Logs
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. System Monitoring
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Error tracking**: Sentry
- **Performance monitoring**: New Relic, DataDog

### 3. Health Check Endpoint
The application includes a health check at `/health` for monitoring services.

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files
- Use platform-specific secret management
- Rotate keys regularly

### 2. Database Security
- Use strong passwords
- Enable connection encryption
- Regular backups

### 3. HTTPS
- Always use HTTPS in production
- Configure proper SSL certificates
- Enable HSTS headers

### 4. Firewall
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

## Backup Strategy

### 1. Database Backup
```bash
# SQLite
cp api_manager.db backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump api_manager > backup_$(date +%Y%m%d).sql
```

### 2. Application Backup
```bash
tar -czf app_backup_$(date +%Y%m%d).tar.gz /var/www/api-manager
```

### 3. Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   sudo chown -R www-data:www-data /var/www/api-manager
   sudo chmod -R 755 /var/www/api-manager
   ```

3. **Database Connection Error**
   - Check DATABASE_URL format
   - Verify database server is running
   - Check firewall settings

4. **Email Not Sending**
   - Verify SMTP credentials
   - Check firewall on port 587
   - Enable "Less secure app access" or use app passwords

### Performance Optimization

1. **Database Optimization**
   - Add database indexes
   - Use connection pooling
   - Implement caching (Redis)

2. **Static Files**
   - Use CDN for static assets
   - Enable gzip compression
   - Implement browser caching

3. **Application Optimization**
   - Use Gunicorn with multiple workers
   - Implement rate limiting
   - Add request caching

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Check network/firewall settings

For additional help, please refer to the platform-specific documentation or open an issue in the repository.