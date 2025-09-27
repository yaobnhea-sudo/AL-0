import { useState, useEffect } from 'react'
import { Database, Download, ExternalLink, FileText, Calendar, Users, HardDrive, Tag } from 'lucide-react'
import { datasetsApi } from '../services/api'
import { Dataset } from '../types'

const datasetCategories = [
  { id: 'all', name: 'All Datasets' },
  { id: 'detection', name: 'Object Detection' },
  { id: 'segmentation', name: 'Segmentation' },
  { id: 'lidar', name: 'LIDAR' },
  { id: 'multimodal', name: 'Multimodal' }
]

const featuredDatasets = [
  {
    id: 'kitti',
    name: 'KITTI',
    description: 'The KITTI Vision Benchmark Suite is a dataset for autonomous driving research',
    type: 'multimodal',
    size: '15 GB',
    samples: 7481,
    classes: ['Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram'],
    format: 'PNG, PCL',
    license: 'CC BY-NC-SA 3.0',
    downloadUrl: 'https://www.cvlibs.net/datasets/kitti/',
    documentation: 'https://www.cvlibs.net/publications/Geiger2013IJRR.pdf',
    image: '/datasets/kitti.jpg'
  },
  {
    id: 'nuscenes',
    name: 'nuScenes',
    description: 'Large-scale autonomous driving dataset with 3D object annotations',
    type: 'multimodal',
    size: '350 GB',
    samples: 40000,
    classes: ['Car', 'Truck', 'Trailer', 'Bus', 'Construction_vehicle', 'Motorcycle', 'Bicycle', 'Pedestrian', 'Traffic_cone'],
    format: 'JPG, PCD',
    license: 'CC BY-NC-SA 4.0',
    downloadUrl: 'https://www.nuscenes.org/',
    documentation: 'https://arxiv.org/abs/1903.11027',
    image: '/datasets/nuscenes.jpg'
  },
  {
    id: 'waymo',
    name: 'Waymo Open Dataset',
    description: 'High-quality autonomous driving dataset with diverse scenarios',
    type: 'multimodal',
    size: '1.2 TB',
    samples: 1000000,
    classes: ['Vehicle', 'Pedestrian', 'Cyclist', 'Sign'],
    format: 'JPG, PCD',
    license: 'Waymo Dataset License',
    downloadUrl: 'https://waymo.com/open/',
    documentation: 'https://arxiv.org/abs/1912.04838',
    image: '/datasets/waymo.jpg'
  },
  {
    id: 'cityscapes',
    name: 'Cityscapes',
    description: 'Large-scale dataset for semantic understanding of urban street scenes',
    type: 'segmentation',
    size: '5 GB',
    samples: 25000,
    classes: ['Road', 'Sidewalk', 'Building', 'Wall', 'Fence', 'Pole', 'Traffic_light', 'Traffic_sign', 'Vegetation', 'Terrain', 'Sky', 'Person', 'Rider', 'Car', 'Truck', 'Bus', 'Train', 'Motorcycle', 'Bicycle'],
    format: 'PNG',
    license: 'CC BY-NC-ND 3.0',
    downloadUrl: 'https://www.cityscapes-dataset.com/',
    documentation: 'https://arxiv.org/abs/1604.01685',
    image: '/datasets/cityscapes.jpg'
  },
  {
    id: 'coco',
    name: 'COCO',
    description: 'Common Objects in Context dataset for object detection and segmentation',
    type: 'detection',
    size: '18 GB',
    samples: 330000,
    classes: ['Person', 'Bicycle', 'Car', 'Motorcycle', 'Airplane', 'Bus', 'Train', 'Truck', 'Boat', 'Traffic_light', 'Fire_hydrant', 'Stop_sign', 'Parking_meter', 'Bench', 'Bird', 'Cat', 'Dog', 'Horse', 'Sheep', 'Cow', 'Elephant', 'Bear', 'Zebra', 'Giraffe', 'Backpack', 'Umbrella', 'Handbag', 'Tie', 'Suitcase', 'Frisbee', 'Skis', 'Snowboard', 'Sports_ball', 'Kite', 'Baseball_bat', 'Baseball_glove', 'Skateboard', 'Surfboard', 'Tennis_racket', 'Bottle', 'Wine_glass', 'Cup', 'Fork', 'Knife', 'Spoon', 'Bowl', 'Banana', 'Apple', 'Sandwich', 'Orange', 'Broccoli', 'Carrot', 'Hot_dog', 'Pizza', 'Donut', 'Cake', 'Chair', 'Couch', 'Potted_plant', 'Bed', 'Dining_table', 'Toilet', 'TV', 'Laptop', 'Mouse', 'Remote', 'Keyboard', 'Cell_phone', 'Microwave', 'Oven', 'Toaster', 'Sink', 'Refrigerator', 'Book', 'Clock', 'Vase', 'Scissors', 'Teddy_bear', 'Hair_drier', 'Toothbrush'],
    format: 'JPG, PNG',
    license: 'CC BY 4.0',
    downloadUrl: 'https://cocodataset.org/',
    documentation: 'https://arxiv.org/abs/1405.0312',
    image: '/datasets/coco.jpg'
  },
  {
    id: 'imagenet',
    name: 'ImageNet',
    description: 'Large-scale image database for visual recognition research',
    type: 'detection',
    size: '150 GB',
    samples: 14000000,
    classes: ['1000 classes'],
    format: 'JPG',
    license: 'ImageNet License',
    downloadUrl: 'https://www.image-net.org/',
    documentation: 'https://arxiv.org/abs/1409.0575',
    image: '/datasets/imagenet.jpg'
  }
]

export function DataDatasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedDataset, setSelectedDataset] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      setLoading(true)
      // For demo purposes, use the featured datasets
      setDatasets(featuredDatasets as Dataset[])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load datasets')
    } finally {
      setLoading(false)
    }
  }

  const filteredDatasets = datasets.filter(dataset => 
    selectedCategory === 'all' || dataset.type === selectedCategory
  )

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'detection': return 'text-blue-600 bg-blue-100'
      case 'segmentation': return 'text-green-600 bg-green-100'
      case 'lidar': return 'text-purple-600 bg-purple-100'
      case 'multimodal': return 'text-orange-600 bg-orange-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const formatFileSize = (size: string) => {
    return size
  }

  const formatSampleCount = (samples: number) => {
    if (samples >= 1000000) {
      return `${(samples / 1000000).toFixed(1)}M`
    } else if (samples >= 1000) {
      return `${(samples / 1000).toFixed(1)}K`
    }
    return samples.toString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading datasets...</p>
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
              Datasets & References
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Explore our curated collection of datasets for autonomous driving and computer vision research
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {datasetCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Datasets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDatasets.map((dataset) => (
            <div
              key={dataset.id}
              onClick={() => setSelectedDataset(dataset)}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:border-primary-200 transition-all duration-200 cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Database className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{dataset.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(dataset.type)}`}>
                      {dataset.type}
                    </span>
                  </div>
                </div>
              </div>

              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {dataset.description}
              </p>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-4 h-4" />
                  <span>{formatFileSize(dataset.size)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>{formatSampleCount(dataset.samples)} samples</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Tag className="w-4 h-4" />
                  <span>{dataset.classes.length} classes</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{dataset.license}</span>
                <div className="flex space-x-2">
                  <a
                    href={dataset.downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Download className="w-4 h-4" />
                  </a>
                  <a
                    href={dataset.documentation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-gray-600"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredDatasets.length === 0 && (
          <div className="text-center py-12">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No datasets found</h3>
            <p className="text-gray-500">Try selecting a different category or check back later.</p>
          </div>
        )}
      </div>

      {/* Dataset Details Modal */}
      {selectedDataset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Database className="w-8 h-8 text-primary-600" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedDataset.name}</h2>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(selectedDataset.type)}`}>
                      {selectedDataset.type}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedDataset(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-600">{selectedDataset.description}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Dataset Information</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Size:</span>
                        <span className="font-medium">{formatFileSize(selectedDataset.size)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Samples:</span>
                        <span className="font-medium">{formatSampleCount(selectedDataset.samples)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Format:</span>
                        <span className="font-medium">{selectedDataset.format}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">License:</span>
                        <span className="font-medium">{selectedDataset.license}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Classes</h3>
                    <div className="max-h-32 overflow-y-auto">
                      <div className="flex flex-wrap gap-1">
                        {selectedDataset.classes.slice(0, 20).map((className: string, index: number) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {className}
                          </span>
                        ))}
                        {selectedDataset.classes.length > 20 && (
                          <span className="px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded">
                            +{selectedDataset.classes.length - 20} more
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <a
                    href={selectedDataset.downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                  >
                    <Download className="w-5 h-5 mr-2" />
                    Download Dataset
                  </a>
                  <a
                    href={selectedDataset.documentation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
                  >
                    <ExternalLink className="w-5 h-5 mr-2" />
                    View Documentation
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
