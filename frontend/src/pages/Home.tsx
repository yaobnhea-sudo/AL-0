import { Link } from 'react-router-dom'
import { 
  Play, 
  Brain, 
  BarChart3, 
  Activity, 
  Database, 
  BookOpen,
  ArrowRight,
  Zap,
  Shield,
  Cpu
} from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'Self-Driving Simulator',
    description: 'Interactive 3D simulation with camera and LIDAR data streaming, real-time model predictions, and scenario testing.',
    link: '/demos',
    color: 'from-blue-500 to-blue-600'
  },
  {
    icon: BarChart3,
    title: 'Object Detection',
    description: 'Upload images and videos for real-time object detection using state-of-the-art YOLOv8 models.',
    link: '/demos',
    color: 'from-green-500 to-green-600'
  },
  {
    icon: Activity,
    title: 'Segmentation',
    description: 'Advanced semantic segmentation with DeepLab models for pixel-level understanding.',
    link: '/demos',
    color: 'from-purple-500 to-purple-600'
  },
  {
    icon: Database,
    title: 'Model Gallery',
    description: 'Explore our collection of pre-trained models with performance metrics and evaluation results.',
    link: '/models',
    color: 'from-orange-500 to-orange-600'
  },
  {
    icon: Cpu,
    title: 'Telemetry Dashboard',
    description: 'Real-time monitoring of system performance, inference latency, and resource utilization.',
    link: '/telemetry',
    color: 'from-red-500 to-red-600'
  },
  {
    icon: BookOpen,
    title: 'Developer Tools',
    description: 'Comprehensive SDK, API documentation, and sample scripts for easy integration.',
    link: '/docs',
    color: 'from-indigo-500 to-indigo-600'
  }
]

const stats = [
  { label: 'Models Available', value: '12+' },
  { label: 'Datasets', value: '8' },
  { label: 'API Endpoints', value: '25+' },
  { label: 'Active Users', value: '1.2K+' }
]

export function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%239C92AC" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              AL-0
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              A comprehensive ML systems platform featuring self-driving simulators, 
              object detection, segmentation, and predictive models.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/demos"
                className="inline-flex items-center px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors duration-200 group"
              >
                <Play className="w-5 h-5 mr-2" />
                Try Demos
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/docs"
                className="inline-flex items-center px-8 py-4 bg-transparent border-2 border-white text-white hover:bg-white hover:text-gray-900 font-semibold rounded-lg transition-colors duration-200"
              >
                <BookOpen className="w-5 h-5 mr-2" />
                Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful ML Capabilities
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Explore our comprehensive suite of machine learning tools and demonstrations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Link
                  key={index}
                  to={feature.link}
                  className="group bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:border-primary-200 transition-all duration-200"
                >
                  <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {feature.description}
                  </p>
                  <div className="flex items-center text-primary-600 font-medium group-hover:translate-x-1 transition-transform">
                    Learn more
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Built with Modern Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Leveraging cutting-edge frameworks and tools for optimal performance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">High Performance</h3>
              <p className="text-gray-600">
                Optimized with ONNX models, GPU acceleration, and efficient inference pipelines
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Privacy & Security</h3>
              <p className="text-gray-600">
                Telemetry opt-out, data anonymization, and secure model serving
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Cpu className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Edge Ready</h3>
              <p className="text-gray-600">
                Quantized models and Docker containers for easy deployment anywhere
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Explore our demos, integrate with our API, or dive into the documentation
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/demos"
              className="inline-flex items-center px-8 py-4 bg-white text-primary-600 hover:bg-gray-100 font-semibold rounded-lg transition-colors duration-200"
            >
              <Play className="w-5 h-5 mr-2" />
              Start with Demos
            </Link>
            <Link
              to="/docs"
              className="inline-flex items-center px-8 py-4 bg-transparent border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold rounded-lg transition-colors duration-200"
            >
              <BookOpen className="w-5 h-5 mr-2" />
              Read Documentation
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
