import { useState } from 'react'
import { Play, Upload, Camera, Video, Brain, Activity, BarChart3 } from 'lucide-react'
import { SelfDrivingSimulator } from '../components/SelfDrivingSimulator'
import { EnhancedSimulator } from '../components/EnhancedSimulator'
import { ImageUploadDemo } from '../components/ImageUploadDemo'
import { EnhancedInferenceDemo } from '../components/EnhancedInferenceDemo'
import { VideoUploadDemo } from '../components/VideoUploadDemo'

const demoTabs = [
  {
    id: 'simulator',
    name: 'Self-Driving Simulator',
    icon: Brain,
    description: 'Interactive 3D simulation with camera and LIDAR data streaming'
  },
  {
    id: 'detection',
    name: 'Object Detection',
    icon: BarChart3,
    description: 'Upload images for real-time object detection'
  },
  {
    id: 'segmentation',
    name: 'Segmentation',
    icon: Activity,
    description: 'Advanced semantic segmentation for pixel-level understanding'
  }
]

export function Demos() {
  const [activeTab, setActiveTab] = useState('simulator')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Interactive Demos
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Experience our ML capabilities through hands-on demonstrations
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {demoTabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-1 py-4 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    isActive
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.name}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Demo Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'simulator' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Enhanced Self-Driving Simulator</h2>
                  <p className="text-gray-600">
                    Advanced 3D simulation with realistic LIDAR data, enhanced visualizations, and real-time ML predictions
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>Live Enhanced Simulation</span>
                </div>
              </div>
              <EnhancedSimulator />
            </div>
          </div>
        )}

        {activeTab === 'detection' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Enhanced Object Detection</h2>
                <p className="text-gray-600">
                  Advanced image analysis with multiple models, confidence visualization, performance metrics, and real-time processing
                </p>
              </div>
              <EnhancedInferenceDemo />
            </div>
          </div>
        )}

        {activeTab === 'segmentation' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Semantic Segmentation</h2>
                <p className="text-gray-600">
                  Upload images for pixel-level semantic segmentation using DeepLab models
                </p>
              </div>
              <VideoUploadDemo />
            </div>
          </div>
        )}
      </div>

      {/* Quick Start Guide */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Quick Start Guide</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Get up and running with our demos in minutes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Play className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">1. Choose a Demo</h3>
              <p className="text-gray-600">
                Select from our self-driving simulator, object detection, or segmentation demos
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Upload className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">2. Upload Content</h3>
              <p className="text-gray-600">
                Upload images or videos, or use our simulated data for the self-driving demo
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Brain className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">3. View Results</h3>
              <p className="text-gray-600">
                See real-time ML predictions with visualizations and performance metrics
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
