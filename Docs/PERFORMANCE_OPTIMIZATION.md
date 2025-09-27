# Performance Optimization Guide

This guide covers comprehensive performance optimization strategies for the AL-0 platform, including ONNX model optimization, quantization, monitoring, and deployment optimizations.

## Table of Contents

1. [Model Optimization](#model-optimization)
2. [Quantization Strategies](#quantization-strategies)
3. [Performance Monitoring](#performance-monitoring)
4. [Deployment Optimizations](#deployment-optimizations)
5. [Edge Deployment](#edge-deployment)
6. [Benchmarking](#benchmarking)
7. [Troubleshooting](#troubleshooting)

## Model Optimization

### ONNX Model Optimization

The platform includes comprehensive ONNX model optimization capabilities:

```python
from app.services.model_optimization import ModelOptimizer

# Initialize optimizer
optimizer = ModelOptimizer()

# Basic optimization
optimized_path = optimizer.optimize_model(
    model_path="models/yolov8n.onnx",
    optimization_level="basic"
)

# Aggressive optimization with quantization
optimized_path = optimizer.optimize_model(
    model_path="models/yolov8n.onnx",
    optimization_level="aggressive"
)
```

### Optimization Levels

1. **Basic Optimization**
   - Constant folding
   - Dead code elimination
   - Common subexpression elimination
   - Graph optimization

2. **Aggressive Optimization**
   - All basic optimizations
   - Quantization (INT8)
   - Advanced graph transformations
   - Memory optimization

### Model Benchmarking

```python
# Benchmark model performance
stats = optimizer.benchmark_model(
    model_path="models/yolov8n.onnx",
    input_shape=(640, 640, 3),
    num_runs=100
)

print(f"Mean latency: {stats['mean_latency_ms']:.2f}ms")
print(f"Throughput: {stats['throughput_fps']:.2f} FPS")
print(f"Model size: {stats['model_size_mb']:.2f} MB")
```

## Quantization Strategies

### Dynamic Quantization

Best for models with dynamic input shapes:

```python
# Dynamic quantization
quantized_path = optimizer.quantize_model(
    model_path="models/yolov8n.onnx",
    quantization_type="dynamic"
)
```

### Static Quantization

Requires calibration data but provides better performance:

```python
# Static quantization with calibration data
quantized_path = optimizer.quantize_model(
    model_path="models/yolov8n.onnx",
    quantization_type="static"
)
```

### Quantization Benefits

- **Size Reduction**: 2-4x smaller models
- **Speed Improvement**: 1.5-3x faster inference
- **Memory Usage**: 2-4x less memory consumption
- **Edge Deployment**: Better suited for mobile/edge devices

## Performance Monitoring

### Real-time Metrics

The platform provides comprehensive real-time monitoring:

```python
# Get system health
health = monitoring_service.get_system_health()

# Get performance summary
summary = monitoring_service.get_performance_summary(hours=1)

# Get metrics export
metrics = monitoring_service.get_metrics_export()
```

### Key Metrics

1. **System Metrics**
   - CPU usage percentage
   - Memory usage percentage
   - GPU usage and memory
   - Disk I/O

2. **Application Metrics**
   - API request latency
   - Model inference time
   - FPS and throughput
   - Error rates

3. **Model Metrics**
   - Inference accuracy
   - Model loading time
   - Memory consumption
   - Batch processing efficiency

### Prometheus Integration

Access Prometheus metrics at `http://localhost:8001/metrics`:

```bash
# Example Prometheus queries
api_request_duration_seconds{quantile="0.95"}
model_inference_duration_seconds{model_id="yolov8n"}
system_cpu_usage_percent
system_memory_usage_percent
```

## Deployment Optimizations

### Docker Optimizations

1. **Multi-stage Builds**
   ```dockerfile
   # Use multi-stage builds to reduce image size
   FROM python:3.9-slim as builder
   # ... build dependencies
   
   FROM python:3.9-slim as runtime
   # ... copy only necessary files
   ```

2. **Layer Caching**
   ```dockerfile
   # Order layers by change frequency
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   ```

3. **Image Optimization**
   ```bash
   # Use distroless images for production
   FROM gcr.io/distroless/python3-debian11
   
   # Optimize image size
   docker build --squash -t autonomous-labs:optimized .
   ```

### Kubernetes Optimizations

1. **Resource Limits**
   ```yaml
   resources:
     requests:
       memory: "512Mi"
       cpu: "250m"
     limits:
       memory: "1Gi"
       cpu: "500m"
   ```

2. **Horizontal Pod Autoscaling**
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: autonomous-labs-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: autonomous-labs
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

3. **Node Affinity**
   ```yaml
   affinity:
     nodeAffinity:
       requiredDuringSchedulingIgnoredDuringExecution:
         nodeSelectorTerms:
         - matchExpressions:
           - key: node-type
             operator: In
             values:
             - gpu-enabled
   ```

## Edge Deployment

### ONNX Runtime Edge

1. **Model Conversion**
   ```python
   # Convert PyTorch model to ONNX
   import torch
   import onnx
   
   model = torch.load('model.pth')
   model.eval()
   
   dummy_input = torch.randn(1, 3, 640, 640)
   torch.onnx.export(
       model,
       dummy_input,
       "model.onnx",
       export_params=True,
       opset_version=11,
       do_constant_folding=True
   )
   ```

2. **Edge Optimization**
   ```python
   # Optimize for edge deployment
   import onnxruntime as ort
   
   # Create session with optimizations
   session = ort.InferenceSession(
       "model.onnx",
       providers=['CPUExecutionProvider'],
       sess_options=ort.SessionOptions()
   )
   
   # Enable optimizations
   session.set_providers(['CPUExecutionProvider'])
   ```

### Mobile Deployment

1. **TensorFlow Lite Conversion**
   ```python
   # Convert ONNX to TensorFlow Lite
   import tf2onnx
   import tensorflow as tf
   
   # Convert ONNX to TensorFlow
   tf_model = tf2onnx.convert.from_onnx("model.onnx")
   
   # Convert to TensorFlow Lite
   converter = tf.lite.TFLiteConverter.from_saved_model(tf_model)
   converter.optimizations = [tf.lite.Optimize.DEFAULT]
   tflite_model = converter.convert()
   
   with open("model.tflite", "wb") as f:
       f.write(tflite_model)
   ```

2. **Core ML Conversion**
   ```python
   # Convert ONNX to Core ML
   import coremltools as ct
   
   # Convert ONNX to Core ML
   coreml_model = ct.convert(
       "model.onnx",
       source="onnx",
       convert_to="mlprogram"
   )
   
   # Save Core ML model
   coreml_model.save("model.mlpackage")
   ```

## Benchmarking

### Performance Testing

1. **Load Testing**
   ```bash
   # Use Apache Bench for load testing
   ab -n 1000 -c 10 http://localhost:8000/api/health
   
   # Use wrk for more advanced testing
   wrk -t12 -c400 -d30s http://localhost:8000/api/health
   ```

2. **Model Benchmarking**
   ```python
   # Benchmark different models
   models = ["yolov8n", "yolov8s", "yolov8m", "yolov8l"]
   
   for model in models:
       stats = optimizer.benchmark_model(
           f"models/{model}.onnx",
           input_shape=(640, 640, 3),
           num_runs=100
       )
       print(f"{model}: {stats['mean_latency_ms']:.2f}ms")
   ```

### Performance Comparison

| Model | Size (MB) | Latency (ms) | Accuracy (mAP) | FPS |
|-------|-----------|--------------|----------------|-----|
| YOLOv8n | 6.2 | 8.5 | 0.85 | 117.6 |
| YOLOv8s | 21.5 | 12.3 | 0.89 | 81.3 |
| YOLOv8m | 49.7 | 18.7 | 0.92 | 53.5 |
| YOLOv8l | 83.7 | 25.2 | 0.94 | 39.7 |

## Troubleshooting

### Common Performance Issues

1. **High Memory Usage**
   - Reduce batch size
   - Use model quantization
   - Implement memory pooling
   - Monitor memory leaks

2. **Slow Inference**
   - Use ONNX optimization
   - Enable GPU acceleration
   - Reduce input resolution
   - Use faster models

3. **High CPU Usage**
   - Optimize data preprocessing
   - Use async processing
   - Implement caching
   - Scale horizontally

### Performance Debugging

1. **Profiling**
   ```python
   # Use cProfile for Python profiling
   import cProfile
   
   cProfile.run('your_function()', 'profile_output.prof')
   
   # Analyze with pstats
   import pstats
   p = pstats.Stats('profile_output.prof')
   p.sort_stats('cumulative').print_stats(10)
   ```

2. **Memory Profiling**
   ```python
   # Use memory_profiler
   from memory_profiler import profile
   
   @profile
   def your_function():
       # Your code here
       pass
   ```

3. **GPU Profiling**
   ```python
   # Use PyTorch profiler
   import torch.profiler as profiler
   
   with profiler.profile(
       activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
       record_shapes=True
   ) as prof:
       # Your model inference code
       pass
   
   print(prof.key_averages().table(sort_by="cuda_time_total"))
   ```

## Best Practices

1. **Model Selection**
   - Choose models based on accuracy/speed trade-offs
   - Use quantized models for edge deployment
   - Consider model ensemble for critical applications

2. **Caching Strategy**
   - Cache model predictions
   - Implement Redis for distributed caching
   - Use CDN for static assets

3. **Monitoring**
   - Set up comprehensive monitoring
   - Use alerting for performance degradation
   - Regular performance reviews

4. **Scaling**
   - Implement horizontal scaling
   - Use load balancers
   - Consider auto-scaling based on metrics

5. **Security**
   - Implement rate limiting
   - Use input validation
   - Monitor for security threats

## Conclusion

This performance optimization guide provides comprehensive strategies for optimizing the Autonomous Labs platform. Regular monitoring, benchmarking, and optimization are essential for maintaining high performance and user satisfaction.

For more detailed information, refer to the specific documentation for each component and consider consulting with performance engineering experts for complex optimization scenarios.
