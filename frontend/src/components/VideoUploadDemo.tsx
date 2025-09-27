import { useState, useRef, useEffect } from 'react'
import { Upload, Play, Pause, Square, Download, Eye, RotateCcw, AlertCircle } from 'lucide-react'
import { inferenceApi } from '../services/api'
import { SegmentationResult } from '../types'

interface SegmentationMask {
  data: number[][]
  width: number
  height: number
  classes: string[]
  colors: string[]
}

export function VideoUploadDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<SegmentationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState('deeplabv3')
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentFrame, setCurrentFrame] = useState(0)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const models = [
    { id: 'deeplabv3', name: 'DeepLabV3', description: 'High accuracy segmentation' },
    { id: 'deeplabv3+', name: 'DeepLabV3+', description: 'Improved boundary refinement' },
    { id: 'pspnet', name: 'PSPNet', description: 'Pyramid scene parsing' },
    { id: 'fcn', name: 'FCN', description: 'Fully convolutional network' },
  ]

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith('video/')) {
        setSelectedFile(file)
        setPreviewUrl(URL.createObjectURL(file))
        setError(null)
        setResult(null)
        setCurrentFrame(0)
        setIsPlaying(false)
      } else {
        setError('Please select a valid video file')
      }
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setError(null)
      setResult(null)
      setCurrentFrame(0)
      setIsPlaying(false)
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
      const response = await inferenceApi.inferVideo(selectedFile, selectedModel)
      // Poll for results
      const pollResult = async () => {
        try {
          const videoResult = await inferenceApi.getVideoResult(response.jobId)
          if (videoResult.status === 'completed' && videoResult.result) {
            // For demo purposes, simulate segmentation result
            const mockResult: SegmentationResult = {
              mask: {
                data: Array.from({ length: 480 }, () => 
                  Array.from({ length: 640 }, () => Math.floor(Math.random() * 20))
                ),
                width: 640,
                height: 480,
                classes: [
                  'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                  'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
                  'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
                  'horse', 'sheep'
                ],
                colors: [
                  '#000000', '#800000', '#000080', '#008000', '#808000', '#800080',
                  '#008080', '#C0C0C0', '#808080', '#FF0000', '#00FF00', '#0000FF',
                  '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#A52A2A', '#FFC0CB',
                  '#800080', '#FFD700'
                ]
              },
              imageWidth: 640,
              imageHeight: 480,
              inferenceTime: 45.2,
              model: selectedModel
            }
            setResult(mockResult)
          } else if (videoResult.status === 'processing') {
            setTimeout(pollResult, 2000)
          } else {
            setError('Video processing failed')
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Processing failed')
        }
      }
      pollResult()
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
    setCurrentFrame(0)
    setIsPlaying(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleVideoTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentFrame(Math.floor(videoRef.current.currentTime * 30)) // Assuming 30 FPS
    }
  }

  const drawSegmentationMask = (canvas: HTMLCanvasElement, mask: SegmentationMask) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const imageData = ctx.createImageData(canvas.width, canvas.height)
    const data = imageData.data

    for (let y = 0; y < canvas.height; y++) {
      for (let x = 0; x < canvas.width; x++) {
        const maskValue = mask.data[y]?.[x] || 0
        const color = mask.colors[maskValue] || '#000000'
        
        const rgb = hexToRgb(color)
        const index = (y * canvas.width + x) * 4
        
        data[index] = rgb.r
        data[index + 1] = rgb.g
        data[index + 2] = rgb.b
        data[index + 3] = 128 // Semi-transparent
      }
    }

    ctx.putImageData(imageData, 0, 0)
  }

  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 }
  }

  useEffect(() => {
    if (result && canvasRef.current) {
      drawSegmentationMask(canvasRef.current, result.mask)
    }
  }, [result])

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
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Video
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
              <div className="relative inline-block">
                <video
                  ref={videoRef}
                  src={previewUrl}
                  className="max-w-full max-h-64 rounded-lg shadow-sm"
                  onTimeUpdate={handleVideoTimeUpdate}
                  onEnded={() => setIsPlaying(false)}
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
              
              <div className="flex justify-center space-x-2">
                <button
                  onClick={togglePlayPause}
                  className="flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                
                <button
                  onClick={handleProcess}
                  disabled={isProcessing}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? 'Processing...' : 'Process Video'}
                </button>
                
                <button
                  onClick={handleReset}
                  className="btn-secondary"
                >
                  <RotateCcw className="w-4 h-4 mr-1" />
                  Reset
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="w-12 h-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Drop a video here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Supports MP4, WebM, MOV up to 100MB
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
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
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Segmentation Classes
            </label>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-2 gap-2">
                {result.mask.classes.map((className, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: result.mask.colors[index] }}
                    />
                    <span className="text-sm text-gray-700">{className}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Performance Metrics
            </label>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Inference Time:</span>
                <span className="font-mono text-blue-600">{result.inferenceTime.toFixed(2)}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Model:</span>
                <span className="font-mono text-gray-900">{result.model}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Resolution:</span>
                <span className="font-mono text-gray-900">{result.imageWidth}x{result.imageHeight}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Classes:</span>
                <span className="font-mono text-gray-900">{result.mask.classes.length}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-4 rounded-lg">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
