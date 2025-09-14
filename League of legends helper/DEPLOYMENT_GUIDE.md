# 🚀 League of Legends Assistant - Deployment Guide

## Quick Start Deployment

### Prerequisites
- Docker and Docker Compose installed
- Riot Games API key (get from [Riot Developer Portal](https://developer.riotgames.com/))

### Option 1: Simple Docker Deployment (Recommended)

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd "League of legends helper"
cp .env.example .env
```

2. **Configure environment variables:**
```bash
# Edit .env file
RIOT_API_KEY=your-riot-api-key-here
NODE_ENV=production
```

3. **Deploy with Docker Compose:**
```bash
# Basic deployment (app only)
docker-compose up -d

# Production deployment (with nginx reverse proxy)
docker-compose --profile production up -d
```

4. **Access the application:**
- Application: http://localhost:3000
- API Health: http://localhost:3001/health
- With nginx: http://localhost (port 80)

### Option 2: Manual Node.js Deployment

1. **Install dependencies:**
```bash
npm install
cd "seneca/react-vite-app"
npm install
```

2. **Build React app:**
```bash
npm run build
```

3. **Set environment variables:**
```bash
export RIOT_API_KEY="your-api-key"
export NODE_ENV="production"
```

4. **Start services:**
```bash
# Terminal 1: Start proxy server
node proxy-server.js

# Terminal 2: Serve React app
cd "seneca/react-vite-app"
npx serve -s dist -l 3000
```

### Option 3: Cloud Platform Deployment

#### Heroku Deployment
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set RIOT_API_KEY=your-api-key
git push heroku main
```

#### Railway Deployment
1. Connect GitHub repository to Railway
2. Set environment variable: `RIOT_API_KEY`
3. Deploy automatically on push

#### DigitalOcean App Platform
1. Create new app from GitHub repository
2. Configure environment variables
3. Set build command: `npm run build`
4. Set run command: `npm start`

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `RIOT_API_KEY` | Yes | Your Riot Games API key | - |
| `NODE_ENV` | No | Environment mode | `development` |
| `PORT` | No | Port for React app | `3000` |
| `PROXY_PORT` | No | Port for API proxy | `3001` |

## Health Checks

- **API Health:** `GET /health`
- **Expected Response:** `{"status": "OK", "message": "Riot API proxy server is running"}`

## Troubleshooting

### Common Issues

1. **API Key Issues:**
   - Ensure your Riot API key is valid and not expired
   - Check rate limits (20 requests/second for development keys)
   - Verify key has correct permissions

2. **Port Conflicts:**
   - Default ports: 3000 (React), 3001 (API)
   - Change ports in docker-compose.yml if needed

3. **CORS Issues:**
   - API proxy handles CORS automatically
   - If using custom deployment, ensure CORS is configured

4. **Build Failures:**
   - Ensure Node.js version 16+ is installed
   - Clear node_modules and reinstall if needed

### Log Access

```bash
# Docker logs
docker-compose logs -f lol-assistant

# Individual service logs
docker logs <container-id>
```

## Performance Optimization

### Production Recommendations

1. **Use nginx reverse proxy** (included in docker-compose.yml)
2. **Enable gzip compression** (configured in nginx.conf)
3. **Set proper cache headers** for static assets
4. **Monitor API rate limits** to avoid throttling
5. **Use environment-specific API keys** (development vs production)

### Scaling

For high traffic deployment:

1. **Horizontal scaling:**
```yaml
services:
  lol-assistant:
    deploy:
      replicas: 3
```

2. **Load balancing:** nginx upstream configuration included
3. **CDN integration:** Serve static assets via CDN
4. **Database caching:** Consider Redis for API response caching

## Security Considerations

1. **API Key Security:**
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **HTTPS in Production:**
   - Uncomment SSL configuration in nginx.conf
   - Obtain SSL certificates (Let's Encrypt recommended)

3. **Rate Limiting:**
   - Implement client-side rate limiting
   - Monitor Riot API usage to avoid bans

## Competition Deployment Notes

For **Seneca Hacks 2025** submission:

1. **Easy Deployment:** Use Docker Compose for one-command deployment
2. **Demo Mode:** Twitch chat analysis works without API keys
3. **Documentation:** See OPEN_SOURCE_ATTRIBUTION.md for component details
4. **Health Monitoring:** Built-in health checks for reliability

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test API connectivity: `curl http://localhost:3001/health`
4. Ensure ports are available and not blocked by firewall