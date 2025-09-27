# Model Directory

This directory contains the ML models used by the Autonomous Labs platform.

## Model Structure

```
models/
├── detection/
│   ├── yolov8n.onnx
│   ├── yolov8s.onnx
│   └── yolov8m.onnx
├── segmentation/
│   ├── deeplabv3.onnx
│   └── deeplabv3plus.onnx
├── lidar/
│   ├── pointpillars.onnx
│   └── pointnet.onnx
└── README.md
```

## Model Formats

All models are stored in ONNX format for optimal performance and cross-platform compatibility.

## Model Loading

Models are automatically loaded by the ModelService when requested. The service will:
1. Check if the model is already loaded in memory
2. If not, load the model from disk
3. Cache the model for future use

## Adding New Models

To add a new model:
1. Place the ONNX file in the appropriate subdirectory
2. Update the model registry in the database
3. The model will be automatically available for inference

## Model Requirements

- Format: ONNX
- Input: Standardized input shapes
- Output: Standardized output format
- Size: Maximum 500MB per model
