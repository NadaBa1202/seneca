# 🚀 Deployment Guide

## Production Deployment Instructions

### 🏗️ Prerequisites
- Node.js 16+ installed on server
- Domain name configured (optional)
- SSL certificate for HTTPS (recommended)
- Riot Games API key (production tier recommended)

## 📋 Deployment Steps

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 for process management
sudo npm install -g pm2
```

### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/NadaBa1202/seneca.git
cd seneca

# Set up League application
cd "League of legends helper"
npm install --production

# Set up frontend
cd seneca/react-vite-app
npm install
npm run build
```

### 3. Environment Configuration
```bash
# Configure proxy server
cd "League of legends helper"
# Edit proxy-server.js to add your production API key
nano proxy-server.js
```

Update the API key in `proxy-server.js`:
```javascript
const API_KEY = 'RGAPI-your-production-api-key-here';
```

### 4. Process Management with PM2
```bash
# Create PM2 ecosystem file
cd "League of legends helper"
```

Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'league-proxy-server',
    script: 'proxy-server.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    }
  }]
};
```

Start the application:
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 5. Nginx Configuration (Optional)
```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/league-analytics
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /path/to/seneca/League\ of\ legends\ helper/seneca/react-vite-app/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/league-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Environment Variables

### Production Environment Setup
Create a production configuration file:

```bash
# /etc/environment
NODE_ENV=production
RIOT_API_KEY=your-production-key
PORT=3001
FRONTEND_URL=https://your-domain.com
```

## 📊 Monitoring & Maintenance

### PM2 Monitoring
```bash
# Check application status
pm2 status
pm2 logs league-proxy-server

# Restart application
pm2 restart league-proxy-server

# Monitor resources
pm2 monit
```

### System Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application logs
pm2 logs --lines 50
```

## 🔒 Security Considerations

### 1. API Key Security
- Use production-tier Riot API key
- Implement rate limiting
- Monitor API usage
- Rotate keys regularly

### 2. Server Security
```bash
# Update packages regularly
sudo apt update && sudo apt upgrade

# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 3. Application Security
- Enable HTTPS only
- Implement CORS properly
- Validate all inputs
- Monitor for security vulnerabilities

## 📈 Performance Optimization

### 1. Frontend Optimization
```bash
# Build with optimization
cd seneca/react-vite-app
npm run build

# Enable gzip compression in Nginx
# Add to nginx.conf:
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 2. Backend Optimization
- Implement caching for frequently requested data
- Use connection pooling for database connections
- Monitor and optimize API response times

### 3. CDN Integration (Optional)
- Serve static assets through CDN
- Cache API responses appropriately
- Implement edge caching

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :3001
   sudo kill -9 <PID>
   ```

2. **Permission Issues**
   ```bash
   sudo chown -R $USER:$USER /path/to/project
   chmod +x proxy-server.js
   ```

3. **API Key Issues**
   - Verify key is valid and not expired
   - Check rate limits
   - Ensure proper environment configuration

4. **Frontend Build Issues**
   ```bash
   cd seneca/react-vite-app
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

## 📱 Mobile Deployment Considerations

- Ensure responsive design works on all devices
- Test touch interactions
- Optimize for mobile performance
- Consider PWA implementation

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    - name: Install dependencies
      run: |
        cd "League of legends helper"
        npm install
        cd seneca/react-vite-app
        npm install
    - name: Build application
      run: |
        cd "League of legends helper/seneca/react-vite-app"
        npm run build
    - name: Deploy to server
      run: |
        # Add your deployment commands here
```

## 📞 Production Support

### Health Checks
- Monitor `/health` endpoint
- Set up uptime monitoring
- Configure alerts for downtime

### Backup Strategy
- Regular database backups (if applicable)
- Configuration file backups
- Log file rotation

### Scaling Considerations
- Monitor resource usage
- Plan for increased traffic during events
- Consider load balancing for high availability

---

**For support with deployment issues, please check the troubleshooting section or create an issue on GitHub.**