# AIOS API Proxy

A Docker-based API proxy that acts as a secure middleman between Streamlit Cloud and your local LM Studio instance.

## Features

- **Secure Proxy**: Protects your local LM Studio from direct external access
- **CORS Support**: Configured for Streamlit Cloud integration
- **Health Monitoring**: Built-in health checks and logging
- **Error Handling**: Robust error handling and timeout management
- **Docker Ready**: Easy deployment with Docker Compose

## Quick Start

### 1. Build and Run

```bash
cd docker-api
docker-compose up --build
```

### 2. Test Connection

```bash
# Health check
curl http://localhost:8000/health

# Get models
curl http://localhost:8000/v1/models

# Test chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### 3. Update Streamlit Portfolio

Change the LM Studio URL in your portfolio from:
```python
LM_STUDIO_URL = "http://192.168.1.21:1234/v1/chat/completions"
```

To:
```python
LM_STUDIO_URL = "http://your-server-ip:8000/v1/chat/completions"
```

## Configuration

### Environment Variables

- `LM_STUDIO_URL`: URL of your LM Studio instance (default: `http://host.docker.internal:1234`)
- `API_TIMEOUT`: Request timeout in seconds (default: 30)

### Docker Compose

The `docker-compose.yml` file includes:
- Port mapping (8000:8000)
- Health checks
- Restart policy
- Network configuration

## Deployment Options

### Local Development
```bash
docker-compose up --build
```

### Production (with your own server)
1. Deploy to a cloud server (AWS, DigitalOcean, etc.)
2. Update `LM_STUDIO_URL` to point to your LM Studio server
3. Configure firewall to allow port 8000
4. Update Streamlit portfolio with server IP

### Cloud Deployment
- **Railway**: `railway deploy`
- **Render**: Connect GitHub repo
- **Heroku**: Add Procfile and deploy
- **DigitalOcean**: Use App Platform

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /v1/models` - Get available models
- `POST /v1/chat/completions` - Chat completions
- `POST /v1/completions` - Text completions
- `POST /v1/embeddings` - Generate embeddings

## Security Notes

- CORS is configured for Streamlit Cloud
- No authentication (add if needed for production)
- Consider rate limiting for production use
- Use HTTPS in production

## Troubleshooting

### Connection Issues
1. Ensure LM Studio is running
2. Check Docker logs: `docker-compose logs`
3. Verify network connectivity: `curl http://host.docker.internal:1234/v1/models`

### Performance
- Adjust `API_TIMEOUT` for slower models
- Monitor Docker resource usage
- Consider load balancing for multiple clients

## Production Checklist

- [ ] Configure HTTPS
- [ ] Add authentication/rate limiting
- [ ] Set up monitoring/logging
- [ ] Configure backup/restart policies
- [ ] Update CORS origins to specific domains
- [ ] Set up health check monitoring
