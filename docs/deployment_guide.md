# Deployment Guide

This guide provides instructions for deploying the DPRG Archive Agent in various environments.

## Prerequisites

1. Python 3.8 or higher
2. Docker (optional)
3. Git
4. Required API keys and credentials

## Environment Setup

### 1. Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### 2. Production Environment

1. System requirements:
   - 4+ CPU cores
   - 8GB+ RAM
   - 50GB+ storage
   - Ubuntu 20.04 LTS or higher

2. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3.8 python3.8-venv nginx
   ```

3. Set up application user:
   ```bash
   sudo useradd -m -s /bin/bash dprg-agent
   sudo usermod -aG sudo dprg-agent
   ```

## Deployment Methods

### 1. Docker Deployment

1. Build the image:
   ```bash
   docker build -t dprg-archive-agent .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name dprg-agent \
     -p 8000:8000 \
     -v /path/to/data:/app/data \
     --env-file .env \
     dprg-archive-agent
   ```

3. Docker Compose:
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
       env_file:
         - .env
       restart: unless-stopped
   ```

### 2. Manual Deployment

1. Clone the repository:
   ```bash
   sudo -u dprg-agent git clone https://github.com/yourusername/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

2. Set up virtual environment:
   ```bash
   python3.8 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

4. Set up systemd service:
   ```ini
   [Unit]
   Description=DPRG Archive Agent
   After=network.target

   [Service]
   User=dprg-agent
   Group=dprg-agent
   WorkingDirectory=/home/dprg-agent/DprgArchiveAgent
   Environment="PATH=/home/dprg-agent/DprgArchiveAgent/venv/bin"
   ExecStart=/home/dprg-agent/DprgArchiveAgent/venv/bin/python -m src.api
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. Enable and start the service:
   ```bash
   sudo systemctl enable dprg-agent
   sudo systemctl start dprg-agent
   ```

## Nginx Configuration

1. Create Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/dprg-agent /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## SSL Configuration

1. Install Certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. Obtain SSL certificate:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Monitoring

### 1. Logging

1. Application logs:
   ```bash
   sudo journalctl -u dprg-agent -f
   ```

2. Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

### 2. Health Checks

1. API health endpoint:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. System monitoring:
   ```bash
   # CPU usage
   top
   
   # Memory usage
   free -m
   
   # Disk usage
   df -h
   ```

## Backup and Recovery

### 1. Data Backup

1. Create backup script:
   ```bash
   #!/bin/bash
   BACKUP_DIR="/path/to/backups"
   DATE=$(date +%Y%m%d)
   
   # Backup data directory
   tar -czf $BACKUP_DIR/data_$DATE.tar.gz /path/to/data
   
   # Backup configuration
   cp .env $BACKUP_DIR/env_$DATE
   ```

2. Schedule backups:
   ```bash
   0 2 * * * /path/to/backup.sh
   ```

### 2. Recovery

1. Restore data:
   ```bash
   tar -xzf data_20240101.tar.gz -C /path/to/data
   ```

2. Restore configuration:
   ```bash
   cp env_20240101 .env
   ```

## Security Considerations

### 1. Firewall Configuration

1. Configure UFW:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

### 2. Application Security

1. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. Regular security audits:
   ```bash
   # Run security checks
   safety check
   bandit -r src/
   ```

## Scaling

### 1. Horizontal Scaling

1. Load balancer configuration:
   ```nginx
   upstream dprg_agent {
       server 127.0.0.1:8000;
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
   }
   ```

2. Multiple instances:
   ```bash
   # Start multiple instances
   python -m src.api --port 8000
   python -m src.api --port 8001
   python -m src.api --port 8002
   ```

### 2. Vertical Scaling

1. Increase resources:
   - Add more CPU cores
   - Increase RAM
   - Upgrade storage

2. Optimize configuration:
   ```python
   # Update worker configuration
   workers = cpu_count() * 2 + 1
   worker_class = 'uvicorn.workers.UvicornWorker'
   ```

## Troubleshooting

### Common Issues

1. Service not starting:
   ```bash
   sudo systemctl status dprg-agent
   sudo journalctl -u dprg-agent -n 50
   ```

2. Connection issues:
   ```bash
   # Check ports
   sudo netstat -tulpn | grep 8000
   
   # Check firewall
   sudo ufw status
   ```

3. Performance issues:
   ```bash
   # Monitor resources
   htop
   
   # Check logs
   tail -f /var/log/nginx/error.log
   ```

## Maintenance

### Regular Tasks

1. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. Clean logs:
   ```bash
   sudo journalctl --vacuum-time=7d
   ```

3. Backup verification:
   ```bash
   # Test backup restoration
   tar -tzf backup.tar.gz
   ```

### Monitoring Tasks

1. Check system health:
   ```bash
   # CPU usage
   top
   
   # Memory usage
   free -m
   
   # Disk usage
   df -h
   ```

2. Monitor application:
   ```bash
   # Check logs
   sudo journalctl -u dprg-agent -f
   
   # Check API
   curl http://localhost:8000/api/v1/health
   ```

## Resources

### Documentation

- [Python Deployment Guide](https://docs.python.org/3/using/unix.html)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

### Tools

- Docker
- Nginx
- Certbot
- Systemd
- UFW 