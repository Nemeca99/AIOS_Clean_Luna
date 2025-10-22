# CARMA Docker Setup

This directory contains a complete Docker setup for the CARMA (Cached Aided Retrieval Mycelium Architecture) system, making it fully portable and reproducible.

## 🐳 Quick Start

### Prerequisites
- Docker Desktop installed and running
- 8GB+ RAM available for Docker
- 10GB+ free disk space

### Build and Test
```bash
# Build the Docker image
docker build -t carma-system .

# Run a quick test
docker run --rm carma-system python human_eval/human_eval_prep.py --sample --questions 5
```

### Using the Management Script
```bash
# Make script executable (Linux/Mac)
chmod +x docker-run.sh

# Build and test
./docker-run.sh build
./docker-run.sh test
```

## 🚀 Available Commands

### Individual Components
```bash
# Human evaluation system
./docker-run.sh human-eval

# Ablation testing
./docker-run.sh ablation

# Luna learning system (requires LM Studio)
./docker-run.sh luna

# Continuous Luna system (real-time output)
./docker-run.sh continuous-luna

# Interactive shell
./docker-run.sh shell
```

### Full Stack with Docker Compose
```bash
# Start all services
./docker-run.sh compose-up

# Stop all services
./docker-run.sh compose-down
```

## 📁 Volume Mounts

The Docker setup uses volume mounts for persistent data:

- `./carma_data:/app/carma_data` - CARMA system data
- `./telemetry_data:/app/telemetry_data` - Performance metrics
- `./ablation_results:/app/ablation_results` - Test results
- `./human_eval:/app/human_eval` - Human evaluation data
- `./seed_corpus:/app/seed_corpus` - Training corpus
- `./reports:/app/reports` - Generated reports

## 🔧 Configuration

### Environment Variables
- `PYTHONPATH=/app` - Python module path
- `CARMA_BASE_DIR=/app/carma_data` - CARMA data directory
- `LM_STUDIO_URL=http://host.docker.internal:1234/v1` - LM Studio API

### LM Studio Integration
To use with LM Studio:
1. Install and start LM Studio on your host machine
2. Load a model and start the API server on port 1234
3. The Docker container will automatically connect to `host.docker.internal:1234`

## 🧪 Testing

### Automated Tests
```bash
# Basic functionality test
docker run --rm carma-system python -c "import sys; print('✓ Python working')"

# Human evaluation test
docker run --rm carma-system python human_eval/human_eval_prep.py --sample --questions 10

# CARMA system test
docker run --rm carma-system python -c "from carma_100_percent_consciousness import CARMA100PercentConsciousness; print('✓ CARMA imports working')"
```

### Manual Testing
```bash
# Interactive shell for manual testing
docker run --rm -it carma-system /bin/bash

# Inside container:
python human_eval/human_eval_prep.py --sample --questions 20
python "Hive Mind/ablation_runner.py" --dry-run
```

## 📊 Services

### CARMA System
- **Container**: `carma-system`
- **Purpose**: Main CARMA consciousness system
- **Command**: `python "Hive Mind/luna_main.py" --mode real_learning --questions 10`

### Continuous Luna System
- **Container**: `carma-continuous-luna`
- **Purpose**: Continuous Luna operation with real-time output
- **Command**: `python "Hive Mind/continuous_real_luna.py"`

### Redis Cache
- **Container**: `carma-redis`
- **Purpose**: Caching and session storage
- **Port**: `6379`

### Human Evaluation
- **Container**: `carma-human-eval`
- **Purpose**: Human evaluation pipeline
- **Command**: `python human_eval/human_eval_prep.py --sample --questions 120`

### Ablation Testing
- **Container**: `carma-ablation`
- **Purpose**: Systematic feature testing
- **Command**: `python "Hive Mind/ablation_runner.py" --dry-run`

## 🔍 Monitoring and Debugging

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker logs carma-system
docker logs carma-redis
```

### Resource Usage
```bash
# Container stats
docker stats

# Image size
docker images carma-system
```

### Debug Mode
```bash
# Run with debug output
docker run --rm -e DEBUG=1 carma-system python "Hive Mind/luna_main.py" --verbose
```

## 🧹 Cleanup

### Remove Everything
```bash
./docker-run.sh clean
```

### Manual Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi carma-system

# Clean up volumes (WARNING: deletes data)
docker volume prune
```

## 📈 Performance

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Optimal**: 16GB RAM, 8 CPU cores

### Optimization Tips
1. Use `--memory` limits to prevent container from consuming all host memory
2. Mount volumes for persistent data to avoid rebuilding
3. Use `--cpus` limits for consistent performance
4. Enable Docker BuildKit for faster builds

## 🔒 Security

### Best Practices
- Container runs as non-root user (`carma`)
- No sensitive data in image layers
- Volume mounts for data persistence
- Network isolation with custom bridge

### Production Considerations
- Use secrets management for API keys
- Enable container scanning
- Implement proper logging
- Set up monitoring and alerting

## 🚀 Deployment

### Local Development
```bash
# Quick start for development
./docker-run.sh build
./docker-run.sh test
```

### CI/CD Integration
```bash
# Build for CI
docker build -t carma-system:ci .

# Run tests in CI
docker run --rm carma-system python -m pytest tests/
```

### Production Deployment
1. Use multi-stage builds for smaller images
2. Implement health checks
3. Set up proper monitoring
4. Use container orchestration (Kubernetes/Docker Swarm)

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [CARMA System Documentation](./README.md)
- [Human Evaluation Guide](./human_eval/README.md)

## 🆘 Troubleshooting

### Common Issues

**Build fails with memory error**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use build with more memory
docker build --memory=8g -t carma-system .
```

**Container can't connect to LM Studio**
```bash
# Check LM Studio is running on host
curl http://localhost:1234/v1/models

# Use host networking
docker run --network=host carma-system python "Hive Mind/luna_main.py"
```

**Permission errors with volumes**
```bash
# Fix ownership
sudo chown -R 1000:1000 ./carma_data
```

**Port conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :6379
netstat -tulpn | grep :8501
```

---

**Need help?** Check the [main README](./README.md) or open an issue in the repository.
