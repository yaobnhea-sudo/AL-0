# AL-0 - Deployment Guide

This guide covers how to deploy the AL-0 platform in various environments.

## Quick Start with Docker

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd autonomous-labs

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker and Docker Compose
- CUDA-compatible GPU (optional, for local inference)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Production Deployment

### Docker Deployment

1. **Build production images:**

```bash
# Build frontend
cd frontend
docker build -t autonomous-labs-frontend .

# Build backend
cd ../backend
docker build -t autonomous-labs-backend .
```

2. **Deploy with Docker Compose:**

```bash
# Use production docker-compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

1. **Create namespace:**

```bash
kubectl create namespace autonomous-labs
```

2. **Apply configurations:**

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/ -n autonomous-labs
```

3. **Check deployment status:**

```bash
kubectl get pods -n autonomous-labs
kubectl get services -n autonomous-labs
```

### Cloud Deployment

#### AWS ECS

1. **Build and push images to ECR:**

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and tag images
docker build -t autonomous-labs-frontend ./frontend
docker build -t autonomous-labs-backend ./backend

# Tag for ECR
docker tag autonomous-labs-frontend:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/autonomous-labs-frontend:latest
docker tag autonomous-labs-backend:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/autonomous-labs-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/autonomous-labs-frontend:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/autonomous-labs-backend:latest
```

2. **Deploy using ECS:**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name autonomous-labs

# Register task definitions
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service --cluster autonomous-labs --service-name autonomous-labs --task-definition autonomous-labs:1 --desired-count 2
```

#### Google Cloud Run

1. **Build and deploy:**

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/autonomous-labs-frontend ./frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/autonomous-labs-backend ./backend

# Deploy to Cloud Run
gcloud run deploy autonomous-labs-frontend --image gcr.io/PROJECT-ID/autonomous-labs-frontend --platform managed --region us-central1
gcloud run deploy autonomous-labs-backend --image gcr.io/PROJECT-ID/autonomous-labs-backend --platform managed --region us-central1
```

## Environment Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# API Configuration
API_V1_STR=/api
PROJECT_NAME=Autonomous Labs API
VERSION=1.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost/autonomous_labs
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Model Configuration
MODEL_CACHE_DIR=./models
MAX_MODEL_SIZE_MB=500

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
ENABLE_GPU=true

# Monitoring
ENABLE_TELEMETRY=true
TELEMETRY_INTERVAL=1
```

### Production Considerations

1. **Security:**
   - Use strong, unique secret keys
   - Enable HTTPS/TLS
   - Configure proper CORS origins
   - Use environment variables for sensitive data

2. **Performance:**
   - Use a production WSGI server (Gunicorn)
   - Configure Redis for caching
   - Use a CDN for static assets
   - Enable gzip compression

3. **Monitoring:**
   - Set up logging aggregation
   - Configure health checks
   - Monitor resource usage
   - Set up alerting

4. **Scaling:**
   - Use load balancers
   - Implement horizontal scaling
   - Use container orchestration
   - Configure auto-scaling

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Change ports in docker-compose.yml
   - Check for running services on ports 3000, 8000

2. **Database connection issues:**
   - Verify database URL
   - Check database server status
   - Ensure proper credentials

3. **Model loading failures:**
   - Check model file paths
   - Verify ONNX model compatibility
   - Check available disk space

4. **WebSocket connection issues:**
   - Verify WebSocket URL
   - Check firewall settings
   - Ensure proper proxy configuration

### Logs

```bash
# View Docker logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View Kubernetes logs
kubectl logs -f deployment/autonomous-labs-backend -n autonomous-labs
kubectl logs -f deployment/autonomous-labs-frontend -n autonomous-labs
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check WebSocket
wscat -c ws://localhost:8000/ws/telemetry
```

## Support

For additional support:

- Check the [README.md](README.md) for general information
- Review the [API documentation](http://localhost:8000/docs) for API details
- Open an issue on GitHub for bug reports
- Contact the development team for enterprise support
