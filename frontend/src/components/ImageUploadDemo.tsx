import { useState, useRef } from 'react'
import { Upload, X, Download, Eye, RotateCcw, AlertCircle } from 'lucide-react'
import { inferenceApi } from '../services/api'
import { DetectionResult } from '../types'

interface DetectionBox {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  class: string
  classId: number
}

export function ImageUploadDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState('yolov8n')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const models = [
    { id: 'yolov8n', name: 'YOLOv8 Nano', description: 'Fastest, smallest model' },
    { id: 'yolov8s', name: 'YOLOv8 Small', description: 'Balanced speed and accuracy' },
    { id: 'yolov8m', name: 'YOLOv8 Medium', description: 'Higher accuracy' },
    { id: 'yolov8l', name: 'YOLOv8 Large', description: 'Best accuracy' },
  ]

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file)
        setPreviewUrl(URL.createObjectURL(file))
        setError(null)
        setResult(null)
      } else {
        setError('Please select a valid image file')
      }
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setError(null)
      setResult(null)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleProcess = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setError(null)

    try {
      const detectionResult = await inferenceApi.inferImage(selectedFile, selectedModel)
      setResult(detectionResult as DetectionResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const drawDetections = (canvas: HTMLCanvasElement, detections: DetectionBox[], imageWidth: number, imageHeight: number) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw detections
    detections.forEach((detection) => {
      const x = (detection.x / imageWidth) * canvas.width
      const y = (detection.y / imageHeight) * canvas.height
      const width = (detection.width / imageWidth) * canvas.width
      const height = (detection.height / imageHeight) * canvas.height

      // Draw bounding box
      ctx.strokeStyle = `hsl(${detection.classId * 137.5}, 70%, 50%)`
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, width, height)

      // Draw label background
      ctx.fillStyle = `hsl(${detection.classId * 137.5}, 70%, 50%)`
      const labelText = `${detection.class} ${(detection.confidence * 100).toFixed(1)}%`
      const labelWidth = ctx.measureText(labelText).width + 8
      ctx.fillRect(x, y - 20, labelWidth, 20)

      // Draw label text
      ctx.fillStyle = 'white'
      ctx.font = '12px Inter, sans-serif'
      ctx.fillText(labelText, x + 4, y - 6)
    })
  }

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Model
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-3 rounded-lg border text-left transition-colors ${
                selectedModel === model.id
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-medium text-sm">{model.name}</div>
              <div className="text-xs text-gray-500">{model.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Upload Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Image
          </label>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              selectedFile
                ? 'border-green-300 bg-green-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {previewUrl ? (
              <div className="space-y-4">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-w-full max-h-64 mx-auto rounded-lg shadow-sm"
                />
                <div className="flex justify-center space-x-2">
                  <button
                    onClick={handleProcess}
                    disabled={isProcessing}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? 'Processing...' : 'Process Image'}
                  </button>
                  <button
                    onClick={handleReset}
                    className="btn-secondary"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Reset
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                <div>
                  <p className="text-lg font-medium text-gray-900">
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
                  className="btn-primary"
                >
                  Choose File
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Detection Results
          </label>
          <div className="bg-gray-50 rounded-lg p-4 min-h-[300px]">
            {error && (
              <div className="flex items-center space-x-2 text-red-600 mb-4">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-gray-900">Detections Found</h3>
                  <span className="text-sm text-gray-500">
                    {result.boxes.length} objects
                  </span>
                </div>

                <div className="space-y-2">
                  {result.boxes.map((detection, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-white rounded border"
                    >
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded"
                          style={{
                            backgroundColor: `hsl(${detection.classId * 137.5}, 70%, 50%)`
                          }}
                        />
                        <span className="font-medium">{detection.class}</span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {(detection.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>

                <div className="text-sm text-gray-600">
                  <div>Inference Time: {result.inferenceTime.toFixed(2)}ms</div>
                  <div>Model: {result.model}</div>
                </div>
              </div>
            )}

            {!result && !error && (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <Eye className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Upload an image to see detection results</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Visualization Canvas */}
      {result && previewUrl && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Visualization
          </label>
          <div className="relative inline-block">
            <img
              src={previewUrl}
              alt="Original"
              className="max-w-full rounded-lg shadow-sm"
            />
            <canvas
              className="absolute top-0 left-0"
              width={result.imageWidth}
              height={result.imageHeight}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain'
              }}
              ref={(canvas) => {
                if (canvas && result) {
                  drawDetections(canvas, result.boxes, result.imageWidth, result.imageHeight)
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
