# Health Check Endpoints

## Quick Reference

The application provides three health check endpoints for monitoring and orchestration:

### Endpoints

| Endpoint | Purpose | Success Code | Failure Code |
|----------|---------|--------------|--------------|
| `/health` | Comprehensive health check | 200 | 503 |
| `/health/live` | Liveness probe | 200 | - |
| `/health/ready` | Readiness probe | 200 | 503 |

### Port
Health check server runs on **port 8080**

### Usage Examples

```bash
# Check overall health
curl http://localhost:8080/health

# Check if server is alive
curl http://localhost:8080/health/live

# Check if ready for traffic
curl http://localhost:8080/health/ready
```

### Health Check Components

The `/health` endpoint validates:
- ✓ AWS environment variables (AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- ✓ Critical dependencies (streamlit, boto3, strands_agents)
- ✓ Application files (app.py, cloud_engineer_agent.py, env_validator.py)

### Response Example

```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T15:00:00Z",
  "application": "cloudeng-strands-agent",
  "checks": {
    "environment": {
      "status": "ok",
      "message": "All required environment variables are set"
    },
    "dependencies": {
      "status": "ok",
      "message": "All critical dependencies are available"
    },
    "files": {
      "status": "ok",
      "message": "All application files present"
    }
  }
}
```

### Status Values

- **healthy**: All checks passed
- **degraded**: Some warnings but functional
- **unhealthy**: Critical errors detected
- **alive**: Server is responding
- **ready**: Ready to accept traffic
- **not_ready**: Not ready for traffic

## Testing

Run the test suite:
```bash
python test_health_check.py
```

Or specify a custom URL:
```bash
python test_health_check.py http://your-server:8080
```

## Docker

The health check is automatically started with the application:
```bash
docker run -p 8501:8501 -p 8080:8080 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  cloudeng-strands-agent
```

## Integration

See README.md for detailed integration examples with:
- Kubernetes liveness/readiness probes
- Docker Compose health checks
- AWS ECS health checks
- Load balancer configurations
