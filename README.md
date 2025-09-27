# AL-0

A comprehensive ML systems demonstration platform featuring self-driving simulators, object detection, segmentation, and predictive models. Built with React, TypeScript, FastAPI, and modern ML frameworks.

## 🚀 Features

### Core Capabilities
- **Self-driving Simulator**: Interactive 3D visualization with WebGL/Three.js, real-time camera and LIDAR data streaming
- **Object Detection**: Upload images/videos for real-time inference using YOLOv8 models
- **Semantic Segmentation**: Advanced pixel-level understanding with DeepLab models
- **LIDAR Processing**: 3D point cloud analysis with PointPillars and PointNet
- **Model Gallery**: Comprehensive showcase of ML models with performance metrics and evaluation results
- **Telemetry Dashboard**: Real-time monitoring of system performance, inference latency, and resource utilization
- **Developer Tools**: Complete SDK, API documentation, and sample scripts

### Technical Features
- **Real-time WebSocket Communication**: Live telemetry and simulation data streaming
- **ONNX Model Support**: Optimized inference with cross-platform compatibility
- **Docker Containerization**: Easy deployment and scaling
- **RESTful API**: Comprehensive API with OpenAPI documentation
- **Responsive UI**: Modern, mobile-friendly interface with Tailwind CSS
- **Type Safety**: Full TypeScript implementation for both frontend and backend

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Models        │
│   React + TS    │◄──►│   FastAPI       │◄──►│   ONNX Models   │
│   Vite + Tailwind│    │   PyTorch       │    │   YOLOv8        │
│   Three.js      │    │   WebSocket     │    │   DeepLab       │
└─────────────────┘    └─────────────────┘    │   PointPillars  │
                                              └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)
- CUDA-compatible GPU (optional, for local inference)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd al-0

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
autonomous-labs/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API and WebSocket services
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── tests/              # Unit tests
│   └── requirements.txt    # Python dependencies
├── models/                  # ML model storage
│   ├── detection/          # Object detection models
│   ├── segmentation/       # Segmentation models
│   └── lidar/              # LIDAR processing models
├── examples/               # Sample client code
│   ├── python_client.py    # Python SDK example
│   └── javascript_client.js # JavaScript SDK example
├── docker-compose.yml      # Docker orchestration
└── README.md              # This file
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /api/models` - List available models
- `GET /api/models/{id}` - Get model details
- `GET /api/models/{id}/metrics` - Get model performance metrics
- `POST /api/infer/image` - Image inference
- `POST /api/infer/video` - Video inference
- `GET /api/infer/video/{job_id}` - Get video inference results
- `GET /api/telemetry` - Current system telemetry
- `GET /api/telemetry/history` - Historical telemetry data
- `GET /api/datasets` - List available datasets
- `GET /api/simulations` - List simulation runs
- `POST /api/simulations` - Create new simulation

### WebSocket Endpoints
- `WS /ws/telemetry` - Real-time telemetry stream
- `WS /ws/sim/{run_id}` - Simulation data stream

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest tests/

# Run frontend tests
cd frontend
npm test

# Run all tests with Docker
docker-compose -f docker-compose.test.yml up --build
```

## 📊 Performance

- **Image Inference**: 5-25ms latency (YOLOv8 Nano)
- **Video Processing**: 10-30 FPS depending on model
- **WebSocket Latency**: <10ms for real-time data
- **API Response Time**: <100ms for most endpoints
- **Memory Usage**: ~2GB for full model suite

## 🔒 Security & Privacy

- **Telemetry Opt-out**: Users can disable data collection
- **Data Anonymization**: Uploaded videos are anonymized
- **Model Bias Disclaimer**: Clear documentation of model limitations
- **Secure API**: Rate limiting and input validation
- **Privacy Controls**: Granular data sharing preferences

## 🌐 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

### Cloud Deployment
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📚 Documentation

- [API Documentation](API.md) - Complete API reference
- [Deployment Guide](DEPLOYMENT.md) - Deployment instructions
- [Developer Guide](frontend/src/pages/DeveloperDocs.tsx) - SDK and integration guide
- [Interactive API Docs](http://localhost:8000/docs) - Swagger UI

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [YOLOv8](https://github.com/ultralytics/ultralytics) for object detection
- [DeepLab](https://github.com/tensorflow/models/tree/master/research/deeplab) for segmentation
- [PointPillars](https://github.com/nutonomy/second.pytorch) for LIDAR processing
- [Three.js](https://threejs.org/) for 3D visualization
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework

## 📞 Support

- 📧 Email: support@autonomouslabs.com
- 🐛 Issues: [GitHub Issues](https://github.com/autonomous-labs/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/autonomous-labs/discussions)
- 📖 Documentation: [docs.autonomouslabs.com](https://docs.autonomouslabs.com)

---

**Built with ❤️ by the Autonomous Labs team**
