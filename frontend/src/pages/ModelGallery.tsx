import { useState, useEffect } from 'react'
import { Brain, BarChart3, Activity, Cpu, Download, Eye, Zap, Clock, HardDrive } from 'lucide-react'
import { modelsApi } from '../services/api'
import { Model, ModelMetrics } from '../types'

const modelTypes = [
  { id: 'all', name: 'All Models', icon: Brain },
  { id: 'detection', name: 'Object Detection', icon: BarChart3 },
  { id: 'segmentation', name: 'Segmentation', icon: Activity },
  { id: 'lidar', name: 'LIDAR Processing', icon: Cpu },
  { id: 'prediction', name: 'Predictive Models', icon: Brain },
]

export function ModelGallery() {
  const [models, setModels] = useState<Model[]>([])
  const [selectedType, setSelectedType] = useState('all')
  const [selectedModel, setSelectedModel] = useState<Model | null>(null)
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadModels()
  }, [])

  const loadModels = async () => {
    try {
      setLoading(true)
      const modelData = await modelsApi.getModels()
      setModels(modelData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load models')
    } finally {
      setLoading(false)
    }
  }

  const handleModelSelect = async (model: Model) => {
    setSelectedModel(model)
    try {
      const modelMetrics = await modelsApi.getModelMetrics(model.id)
      setMetrics(modelMetrics)
    } catch (err) {
      console.error('Failed to load model metrics:', err)
    }
  }

  const filteredModels = models.filter(model => 
    selectedType === 'all' || model.type === selectedType
  )

  const getModelIcon = (type: string) => {
    const typeConfig = modelTypes.find(t => t.id === type)
    return typeConfig?.icon || Brain
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100'
      case 'training': return 'text-yellow-600 bg-yellow-100'
      case 'deprecated': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading models...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Model Gallery
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Explore our collection of pre-trained models with performance metrics and evaluation results
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Model List */}
          <div className="lg:col-span-2">
            {/* Filter Tabs */}
            <div className="mb-6">
              <div className="flex flex-wrap gap-2">
                {modelTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <button
                      key={type.id}
                      onClick={() => setSelectedType(type.id)}
                      className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                        selectedType === type.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {type.name}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Models Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredModels.map((model) => {
                const Icon = getModelIcon(model.type)
                return (
                  <div
                    key={model.id}
                    onClick={() => handleModelSelect(model)}
                    className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:border-primary-200 transition-all duration-200 cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                          <Icon className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{model.name}</h3>
                          <p className="text-sm text-gray-500">{model.framework}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(model.status)}`}>
                        {model.status}
                      </span>
                    </div>

                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {model.description}
                    </p>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Accuracy:</span>
                        <span className="ml-1 font-medium text-green-600">{(model.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Latency:</span>
                        <span className="ml-1 font-medium text-blue-600">{model.latency}ms</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Size:</span>
                        <span className="ml-1 font-medium text-gray-900">{model.size}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Version:</span>
                        <span className="ml-1 font-medium text-gray-900">{model.version}</span>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Updated {new Date(model.updatedAt).toLocaleDateString()}</span>
                      </div>
                      <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
                        View Details
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>

            {filteredModels.length === 0 && (
              <div className="text-center py-12">
                <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No models found</h3>
                <p className="text-gray-500">Try selecting a different category or check back later.</p>
              </div>
            )}
          </div>

          {/* Model Details Sidebar */}
          <div className="lg:col-span-1">
            {selectedModel ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">Model Details</h3>
                  <button
                    onClick={() => setSelectedModel(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Basic Information</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Name:</span>
                        <span className="font-medium">{selectedModel.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Type:</span>
                        <span className="font-medium capitalize">{selectedModel.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Framework:</span>
                        <span className="font-medium">{selectedModel.framework}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Version:</span>
                        <span className="font-medium">{selectedModel.version}</span>
                      </div>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  {metrics && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Performance Metrics</h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <BarChart3 className="w-4 h-4 text-blue-600" />
                            <span className="text-sm text-gray-600">mAP</span>
                          </div>
                          <span className="font-mono text-sm font-medium">{metrics.mAP.toFixed(3)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Activity className="w-4 h-4 text-green-600" />
                            <span className="text-sm text-gray-600">IoU</span>
                          </div>
                          <span className="font-mono text-sm font-medium">{metrics.IoU.toFixed(3)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Zap className="w-4 h-4 text-yellow-600" />
                            <span className="text-sm text-gray-600">Precision</span>
                          </div>
                          <span className="font-mono text-sm font-medium">{metrics.precision.toFixed(3)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-purple-600" />
                            <span className="text-sm text-gray-600">Recall</span>
                          </div>
                          <span className="font-mono text-sm font-medium">{metrics.recall.toFixed(3)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Brain className="w-4 h-4 text-red-600" />
                            <span className="text-sm text-gray-600">F1 Score</span>
                          </div>
                          <span className="font-mono text-sm font-medium">{metrics.f1Score.toFixed(3)}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="space-y-3">
                    <button className="w-full btn-primary">
                      <Download className="w-4 h-4 mr-2" />
                      Download Model
                    </button>
                    <button className="w-full btn-secondary">
                      <Eye className="w-4 h-4 mr-2" />
                      View Documentation
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Model</h3>
                <p className="text-gray-500">Choose a model from the gallery to view detailed information and metrics.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
