# AL-0 API Documentation

This document provides comprehensive API documentation for the AL-0 platform.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.autonomouslabs.com`

## Authentication

Currently, the API does not require authentication for demo purposes. In production, you would use:

```bash
# Add API key to headers
Authorization: Bearer your-api-key-here
```

## API Endpoints

### Models

#### Get All Models
```http
GET /api/models
```

**Query Parameters:**
- `model_type` (optional): Filter by model type (`detection`, `segmentation`, `lidar`, `prediction`)
- `status` (optional): Filter by status (`active`, `training`, `deprecated`)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "yolov8n",
      "name": "YOLOv8 Nano",
      "type": "detection",
      "description": "Ultra-fast object detection model",
      "version": "8.0.0",
      "framework": "onnx",
      "status": "active",
      "accuracy": 0.85,
      "latency": 8.5,
      "size": "6.2MB",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Get Model Details
```http
GET /api/models/{model_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "yolov8n",
    "name": "YOLOv8 Nano",
    "type": "detection",
    "description": "Ultra-fast object detection model",
    "version": "8.0.0",
    "framework": "onnx",
    "status": "active",
    "accuracy": 0.85,
    "latency": 8.5,
    "size": "6.2MB",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Get Model Metrics
```http
GET /api/models/{model_id}/metrics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "model_id": "yolov8n",
    "mAP": 0.85,
    "IoU": 0.78,
    "precision": 0.82,
    "recall": 0.79,
    "f1_score": 0.80,
    "confusion_matrix": [[100, 5], [3, 92]],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Inference

#### Image Inference
```http
POST /api/infer/image
```

**Form Data:**
- `file`: Image file (required)
- `model_id`: Model ID (required)
- `confidence_threshold`: Confidence threshold (optional, default: 0.5)

**Response:**
```json
{
  "success": true,
  "data": {
    "boxes": [
      {
        "x": 100,
        "y": 150,
        "width": 200,
        "height": 300,
        "confidence": 0.85,
        "class_name": "car",
        "class_id": 2
      }
    ],
    "image_width": 640,
    "image_height": 480,
    "inference_time": 8.5,
    "model": "yolov8n"
  },
  "message": "Image processed successfully"
}
```

#### Video Inference
```http
POST /api/infer/video
```

**Form Data:**
- `file`: Video file (required)
- `model_id`: Model ID (required)
- `confidence_threshold`: Confidence threshold (optional, default: 0.5)

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "message": "Video processing started"
}
```

#### Get Video Result
```http
GET /api/infer/video/{job_id}
```

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "status": "completed",
  "result": [
    {
      "boxes": [...],
      "image_width": 640,
      "image_height": 480,
      "inference_time": 8.5,
      "model": "yolov8n"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Simulations

#### Get Simulations
```http
GET /api/simulations
```

**Query Parameters:**
- `status` (optional): Filter by status
- `limit` (optional): Number of results (default: 10)
- `offset` (optional): Number to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "sim-123",
      "name": "Highway Test",
      "status": "running",
      "config": {
        "scenario": "highway",
        "weather": "clear",
        "time_of_day": "day",
        "traffic": "medium",
        "models": ["yolov8n"]
      },
      "start_time": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Create Simulation
```http
POST /api/simulations
```

**Request Body:**
```json
{
  "name": "Highway Test",
  "config": {
    "scenario": "highway",
    "weather": "clear",
    "time_of_day": "day",
    "traffic": "medium",
    "models": ["yolov8n"],
    "duration": 60
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "sim-123",
    "name": "Highway Test",
    "status": "pending",
    "config": {...},
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Simulation created successfully"
}
```

#### Start Simulation
```http
POST /api/simulations/{run_id}/start
```

**Response:**
```json
{
  "success": true,
  "message": "Simulation sim-123 started",
  "run_id": "sim-123"
}
```

### Telemetry

#### Get Current Telemetry
```http
GET /api/telemetry
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-01T00:00:00Z",
    "fps": 30.5,
    "latency": 15.2,
    "cpu_usage": 45.0,
    "gpu_usage": 60.0,
    "memory_usage": 70.0,
    "model_inference": {
      "detection": 8.5,
      "segmentation": 25.3,
      "lidar": 12.1
    }
  }
}
```

#### Get Telemetry History
```http
GET /api/telemetry/history
```

**Query Parameters:**
- `start_time` (optional): Start time (ISO format)
- `end_time` (optional): End time (ISO format)
- `limit` (optional): Number of results (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "fps": 30.5,
      "latency": 15.2,
      "cpu_usage": 45.0,
      "gpu_usage": 60.0,
      "memory_usage": 70.0,
      "model_inference": {...}
    }
  ],
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-01-01T01:00:00Z",
  "total": 100
}
```

### Datasets

#### Get Datasets
```http
GET /api/datasets
```

**Query Parameters:**
- `dataset_type` (optional): Filter by type
- `limit` (optional): Number of results (default: 10)
- `offset` (optional): Number to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "kitti",
      "name": "KITTI",
      "description": "The KITTI Vision Benchmark Suite",
      "type": "multimodal",
      "size": "15 GB",
      "samples": 7481,
      "classes": ["Car", "Van", "Truck", "Pedestrian"],
      "format": "PNG, PCL",
      "license": "CC BY-NC-SA 3.0",
      "download_url": "https://www.cvlibs.net/datasets/kitti/",
      "documentation": "https://www.cvlibs.net/publications/Geiger2013IJRR.pdf"
    }
  ],
  "total": 1
}
```

## WebSocket Endpoints

### Telemetry Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'telemetry') {
    console.log('FPS:', data.data.fps);
    console.log('Latency:', data.data.latency);
  }
};
```

### Simulation Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/sim/sim-123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'simulation_data') {
    console.log('Frame:', data.frame_number);
    console.log('Detections:', data.detections);
  }
};
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "message": "Human-readable description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

API requests are rate limited to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## SDK Examples

### Python
```python
from autonomous_labs import Client

client = Client(api_key="your-api-key")

# Image inference
result = client.infer_image("image.jpg", "yolov8n")
print(f"Found {len(result.boxes)} objects")

# Video inference
job = client.infer_video("video.mp4", "yolov8n")
result = client.get_video_result(job.job_id)
```

### JavaScript
```javascript
import { AutonomousLabsClient } from '@autonomous-labs/sdk';

const client = new AutonomousLabsClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.autonomouslabs.com'
});

// Image inference
const result = await client.inferImage(file, 'yolov8n');
console.log(`Found ${result.boxes.length} objects`);

// Video inference
const job = await client.inferVideo(file, 'yolov8n');
const result = await client.getVideoResult(job.jobId);
```

## Support

For API support:
- Check the [Interactive API Documentation](http://localhost:8000/docs)
- Review the [Deployment Guide](DEPLOYMENT.md)
- Open an issue on GitHub
- Contact the development team
