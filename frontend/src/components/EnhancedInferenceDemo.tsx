import { useState, useRef, useCallback } from 'react'
import { Upload, X, Download, Eye, RotateCcw, AlertCircle, Zap, BarChart3, Activity, Cpu, Clock } from 'lucide-react'
import { inferenceApi } from '../services/api'
import { DetectionResult, SegmentationResult } from '../types'

interface EnhancedDetectionBox {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  class: string
  classId: number
  velocity?: [number, number, number]
  trackId?: number
}

interface InferenceMetrics {
  totalInferences: number
  averageLatency: number
  successRate: number
  totalProcessingTime: number
  modelsUsed: string[]
}

export function EnhancedInferenceDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<DetectionResult | SegmentationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState('yolov8n')
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5)
  const [showMetrics, setShowMetrics] = useState(false)
  const [inferenceHistory, setInferenceHistory] = useState<InferenceMetrics>({
    totalInferences: 0,
    averageLatency: 0,
    successRate: 100,
    totalProcessingTime: 0,
    modelsUsed: []
  })
  const [processingSteps, setProcessingSteps] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const models = [
    { 
      id: 'yolov8n', 
      name: 'YOLOv8 Nano', 
      description: 'Ultra-fast, smallest model',
      accuracy: 0.85,
      latency: 8.5,
      size: '6.2MB',
      color: 'blue'
    },
    { 
      id: 'yolov8s', 
      name: 'YOLOv8 Small', 
      description: 'Balanced speed and accuracy',
      accuracy: 0.89,
      latency: 12.3,
      size: '21.5MB',
      color: 'green'
    },
    { 
      id: 'yolov8m', 
      name: 'YOLOv8 Medium', 
      description: 'Higher accuracy model',
      accuracy: 0.92,
      latency: 18.7,
      size: '49.7MB',
      color: 'purple'
    },
    { 
      id: 'deeplabv3', 
      name: 'DeepLabV3', 
      description: 'Semantic segmentation',
      accuracy: 0.94,
      latency: 45.2,
      size: '156MB',
      color: 'orange'
    }
  ]

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file)
        setPreviewUrl(URL.createObjectURL(file))
        setError(null)
        setResult(null)
        setProcessingSteps([])
      } else {
        setError('Please select a valid image file')
      }
    }
  }, [])

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setError(null)
      setResult(null)
      setProcessingSteps([])
    }
  }, [])

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }, [])

  const simulateProcessingSteps = useCallback(() => {
    const steps = [
      'Loading model...',
      'Preprocessing image...',
      'Running inference...',
      'Post-processing results...',
      'Generating visualizations...'
    ]
    
    setProcessingSteps([])
    steps.forEach((step, index) => {
      setTimeout(() => {
        setProcessingSteps(prev => [...prev, step])
      }, index * 800)
    })
  }, [])

  const handleProcess = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)
    setProcessingSteps([])
    simulateProcessingSteps()

    try {
      const startTime = Date.now()
      const detectionResult = await inferenceApi.inferImage(selectedFile, selectedModel)
      const endTime = Date.now()
      
      setResult(detectionResult as DetectionResult)
      
      // Update metrics
      const latency = endTime - startTime
      setInferenceHistory(prev => ({
        totalInferences: prev.totalInferences + 1,
        averageLatency: (prev.averageLatency * prev.totalInferences + latency) / (prev.totalInferences + 1),
        successRate: 100, // Assuming success for now
        totalProcessingTime: prev.totalProcessingTime + latency,
        modelsUsed: prev.modelsUsed.includes(selectedModel) ? prev.modelsUsed : [...prev.modelsUsed, selectedModel]
      }))
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed')
      setInferenceHistory(prev => ({
        ...prev,
        successRate: (prev.successRate * prev.totalInferences) / (prev.totalInferences + 1)
      }))
    } finally {
      setIsProcessing(false)
      setProcessingSteps([])
    }
  }

  const handleReset = useCallback(() => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setError(null)
    setProcessingSteps([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [])

  const drawEnhancedDetections = useCallback((canvas: HTMLCanvasElement, detections: EnhancedDetectionBox[], imageWidth: number, imageHeight: number) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw detections with enhanced visualization
    detections.forEach((detection, index) => {
      const x = (detection.x / imageWidth) * canvas.width
      const y = (detection.y / imageHeight) * canvas.height
      const width = (detection.width / imageWidth) * canvas.width
      const height = (detection.height / imageHeight) * canvas.height

      // Color based on confidence and class
      const confidence = detection.confidence
      const hue = (detection.classId * 137.5) % 360
      const saturation = 70 + (confidence * 30)
      const lightness = 50 + (confidence * 20)
      
      ctx.strokeStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
      ctx.fillStyle = `hsla(${hue}, ${saturation}%, ${lightness}%, 0.1)`
      ctx.lineWidth = 3
      
      // Draw bounding box with rounded corners
      const radius = 5
      ctx.beginPath()
      ctx.roundRect(x, y, width, height, radius)
      ctx.fill()
      ctx.stroke()
      
      // Draw confidence bar
      const barHeight = 4
      const barWidth = width * confidence
      ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
      ctx.fillRect(x, y - barHeight - 2, barWidth, barHeight)
      
      // Draw label background
      const labelText = `${detection.class} ${(confidence * 100).toFixed(1)}%`
      ctx.font = 'bold 12px Inter, sans-serif'
      const labelWidth = ctx.measureText(labelText).width + 12
      const labelHeight = 20
      
      ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
      ctx.fillRect(x, y - labelHeight - 6, labelWidth, labelHeight)
      
      // Draw label text
      ctx.fillStyle = 'white'
      ctx.textAlign = 'left'
      ctx.fillText(labelText, x + 6, y - 8)
      
      // Draw track ID if available
      if (detection.trackId !== undefined) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
        ctx.font = '10px Inter, sans-serif'
        ctx.fillText(`ID: ${detection.trackId}`, x + 6, y + height - 6)
      }
    })
  }, [])

  // Update canvas when result changes
  React.useEffect(() => {
    if (result && canvasRef.current && 'boxes' in result) {
      drawEnhancedDetections(canvasRef.current, result.boxes, result.imageWidth, result.imageHeight)
    }
  }, [result, drawEnhancedDetections])

  return (
    <div className="space-y-6">
      {/* Enhanced Model Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Model
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-4 rounded-xl border-2 text-left transition-all duration-200 ${
                selectedModel === model.id
                  ? 'border-primary-500 bg-primary-50 shadow-lg scale-105'
                  : 'border-gray-300 hover:border-gray-400 hover:shadow-md'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <div className={`w-3 h-3 rounded-full bg-${model.color}-500`}></div>
                <span className="font-semibold text-gray-900">{model.name}</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{model.description}</p>
              <div className="space-y-1 text-xs text-gray-500">
                <div className="flex justify-between">
                  <span>Accuracy:</span>
                  <span className="font-medium">{(model.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Latency:</span>
                  <span className="font-medium">{model.latency}ms</span>
                </div>
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span className="font-medium">{model.size}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Confidence Threshold Slider */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Confidence Threshold: {(confidenceThreshold * 100).toFixed(0)}%
        </label>
        <input
          type="range"
          min="0.1"
          max="1.0"
          step="0.05"
          value={confidenceThreshold}
          onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>10%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Enhanced Upload Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Image
          </label>
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
              selectedFile
                ? 'border-green-300 bg-green-50 shadow-lg'
                : 'border-gray-300 hover:border-gray-400 hover:shadow-md'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {previewUrl ? (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-w-full max-h-64 mx-auto rounded-lg shadow-sm"
                  />
                  {result && (
                    <canvas
                      ref={canvasRef}
                      className="absolute top-0 left-0 w-full h-full"
                      width={result.imageWidth}
                      height={result.imageHeight}
                    />
                  )}
                </div>
                
                <div className="flex justify-center space-x-3">
                  <button
                    onClick={handleProcess}
                    disabled={isProcessing}
                    className="flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Process Image
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleReset}
                    className="flex items-center px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition-colors"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                <div>
                  <p className="text-xl font-medium text-gray-900 mb-2">
                    Drop an image here, or click to select
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports JPG, PNG, WebP up to 10MB
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
                >
                  Choose File
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Enhanced Results */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Inference Results
            </label>
            <button
              onClick={() => setShowMetrics(!showMetrics)}
              className="flex items-center px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
            >
              <BarChart3 className="w-4 h-4 mr-1" />
              {showMetrics ? 'Hide' : 'Show'} Metrics
            </button>
          </div>
          
          <div className="bg-gray-50 rounded-xl p-6 min-h-[300px]">
            {error && (
              <div className="flex items-center space-x-2 text-red-600 mb-4 p-3 bg-red-50 rounded-lg">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            {isProcessing && (
              <div className="space-y-4">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
                  <p className="text-sm text-gray-600">Processing your image...</p>
                </div>
                {processingSteps.length > 0 && (
                  <div className="space-y-2">
                    {processingSteps.map((step, index) => (
                      <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Detections Found</h3>
                  <span className="text-sm text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
                    {result.boxes?.length || 0} objects
                  </span>
                </div>

                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {result.boxes?.map((detection, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-sm transition-shadow"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{
                            backgroundColor: `hsl(${detection.classId * 137.5}, 70%, 50%)`
                          }}
                        />
                        <div>
                          <span className="font-medium text-gray-900">{detection.class}</span>
                          {detection.trackId && (
                            <span className="text-xs text-gray-500 ml-2">ID: {detection.trackId}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${detection.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700 w-12 text-right">
                          {(detection.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Inference Time:</span>
                    <span className="font-medium text-blue-600">{result.inferenceTime.toFixed(2)}ms</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Cpu className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">Model:</span>
                    <span className="font-medium text-gray-900">{result.model}</span>
                  </div>
                </div>
              </div>
            )}

            {!result && !error && !isProcessing && (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <Eye className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Upload an image to see inference results</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Metrics Panel */}
      {showMetrics && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Inference Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">{inferenceHistory.totalInferences}</div>
              <div className="text-sm text-gray-600">Total Inferences</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{inferenceHistory.averageLatency.toFixed(1)}ms</div>
              <div className="text-sm text-gray-600">Avg Latency</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{inferenceHistory.successRate.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{inferenceHistory.modelsUsed.length}</div>
              <div className="text-sm text-gray-600">Models Used</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
