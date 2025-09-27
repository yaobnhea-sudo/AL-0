// Model types
export interface Model {
  id: string
  name: string
  type: 'detection' | 'segmentation' | 'lidar' | 'prediction'
  description: string
  version: string
  accuracy: number
  latency: number
  size: string
  framework: string
  status: 'active' | 'training' | 'deprecated'
  createdAt: string
  updatedAt: string
}

// Detection types
export interface DetectionBox {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  class: string
  classId: number
}

export interface DetectionResult {
  boxes: DetectionBox[]
  imageWidth: number
  imageHeight: number
  inferenceTime: number
  model: string
}

// Segmentation types
export interface SegmentationMask {
  data: number[][]
  width: number
  height: number
  classes: string[]
  colors: string[]
}

export interface SegmentationResult {
  mask: SegmentationMask
  imageWidth: number
  imageHeight: number
  inferenceTime: number
  model: string
}

// LIDAR types
export interface PointCloud {
  points: number[][]
  colors?: number[][]
  intensities?: number[]
}

export interface LidarResult {
  pointCloud: PointCloud
  detections: DetectionBox[]
  inferenceTime: number
  model: string
}

// Telemetry types
export interface TelemetryData {
  timestamp: string
  fps: number
  latency: number
  cpuUsage: number
  gpuUsage: number
  memoryUsage: number
  modelInference: {
    detection: number
    segmentation: number
    lidar: number
  }
}

// Simulation types
export interface SimulationRun {
  id: string
  name: string
  status: 'running' | 'paused' | 'stopped' | 'completed'
  startTime: string
  endTime?: string
  duration?: number
  config: SimulationConfig
}

export interface SimulationConfig {
  scenario: string
  weather: string
  timeOfDay: string
  traffic: string
  models: string[]
}

// API Response types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ModelMetrics {
  mAP: number
  IoU: number
  precision: number
  recall: number
  f1Score: number
  confusionMatrix: number[][]
}

// Upload types
export interface UploadProgress {
  fileId: string
  fileName: string
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
}

// Dataset types
export interface Dataset {
  id: string
  name: string
  description: string
  type: 'detection' | 'segmentation' | 'lidar' | 'multimodal'
  size: string
  samples: number
  classes: string[]
  format: string
  license: string
  downloadUrl: string
  documentation: string
}
