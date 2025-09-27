import { useState } from 'react'
import { BookOpen, Code, Download, ExternalLink, Copy, Check } from 'lucide-react'

const sections = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: BookOpen,
    subsections: [
      { id: 'installation', title: 'Installation' },
      { id: 'quick-start', title: 'Quick Start' },
      { id: 'configuration', title: 'Configuration' }
    ]
  },
  {
    id: 'api-reference',
    title: 'API Reference',
    icon: Code,
    subsections: [
      { id: 'authentication', title: 'Authentication' },
      { id: 'endpoints', title: 'Endpoints' },
      { id: 'websockets', title: 'WebSockets' },
      { id: 'rate-limits', title: 'Rate Limits' }
    ]
  },
  {
    id: 'sdks',
    title: 'SDKs & Libraries',
    icon: Download,
    subsections: [
      { id: 'python-sdk', title: 'Python SDK' },
      { id: 'javascript-sdk', title: 'JavaScript SDK' },
      { id: 'examples', title: 'Code Examples' }
    ]
  },
  {
    id: 'deployment',
    title: 'Deployment',
    icon: ExternalLink,
    subsections: [
      { id: 'docker', title: 'Docker' },
      { id: 'kubernetes', title: 'Kubernetes' },
      { id: 'edge-deployment', title: 'Edge Deployment' }
    ]
  }
]

const codeExamples = {
  'python-sdk': `# Install the Python SDK
pip install autonomous-labs-sdk

# Basic usage
from autonomous_labs import Client

client = Client(api_key="your-api-key")

# Image inference
result = client.infer_image("path/to/image.jpg", model_id="yolov8n")
print(f"Found {len(result.boxes)} objects")

# Video inference
job = client.infer_video("path/to/video.mp4", model_id="deeplabv3")
result = client.get_video_result(job.job_id)

# Real-time telemetry
def on_telemetry(data):
    print(f"FPS: {data.fps}, Latency: {data.latency}ms")

client.subscribe_telemetry(on_telemetry)`,
  
  'javascript-sdk': `// Install the JavaScript SDK
npm install @autonomous-labs/sdk

// Basic usage
import { AutonomousLabsClient } from '@autonomous-labs/sdk';

const client = new AutonomousLabsClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.autonomouslabs.com'
});

// Image inference
const result = await client.inferImage(file, 'yolov8n');
console.log(\`Found \${result.boxes.length} objects\`);

// Video inference
const job = await client.inferVideo(file, 'deeplabv3');
const result = await client.getVideoResult(job.jobId);

// Real-time telemetry
client.subscribeTelemetry((data) => {
  console.log(\`FPS: \${data.fps}, Latency: \${data.latency}ms\`);
});`,
  
  'docker': `# Docker Compose for local development
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./models:/app/models

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

# Run with Docker Compose
docker-compose up --build`,
  
  'kubernetes': `# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autonomous-labs-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autonomous-labs-backend
  template:
    metadata:
      labels:
        app: autonomous-labs-backend
    spec:
      containers:
      - name: backend
        image: autonomous-labs/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: autonomous-labs-backend-service
spec:
  selector:
    app: autonomous-labs-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer`
}

export function DeveloperDocs() {
  const [activeSection, setActiveSection] = useState('getting-started')
  const [activeSubsection, setActiveSubsection] = useState('installation')
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyToClipboard = async (code: string, key: string) => {
    try {
      await navigator.clipboard.writeText(code)
      setCopiedCode(key)
      setTimeout(() => setCopiedCode(null), 2000)
    } catch (err) {
      console.error('Failed to copy code:', err)
    }
  }

  const renderContent = () => {
    switch (activeSubsection) {
      case 'installation':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Installation</h2>
            <p className="text-gray-600">
              Get started with Autonomous Labs by installing our SDKs and setting up your development environment.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Prerequisites</h3>
              <ul className="text-blue-800 space-y-1">
                <li>• Python 3.9+ or Node.js 18+</li>
                <li>• Docker and Docker Compose</li>
                <li>• CUDA-compatible GPU (optional, for local inference)</li>
              </ul>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">Python SDK</h3>
              <div className="bg-gray-900 rounded-lg p-4 relative">
                <button
                  onClick={() => copyToClipboard('pip install autonomous-labs-sdk', 'python-install')}
                  className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
                >
                  {copiedCode === 'python-install' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
                <code className="text-green-400">pip install autonomous-labs-sdk</code>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">JavaScript SDK</h3>
              <div className="bg-gray-900 rounded-lg p-4 relative">
                <button
                  onClick={() => copyToClipboard('npm install @autonomous-labs/sdk', 'js-install')}
                  className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
                >
                  {copiedCode === 'js-install' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
                <code className="text-green-400">npm install @autonomous-labs/sdk</code>
              </div>
            </div>
          </div>
        )

      case 'quick-start':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Quick Start</h2>
            <p className="text-gray-600">
              Learn how to make your first API call and process an image in under 5 minutes.
            </p>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">1. Get Your API Key</h3>
                <p className="text-gray-600 mb-4">
                  Sign up for a free account and get your API key from the dashboard.
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <code className="text-sm text-gray-700">API_KEY=your-api-key-here</code>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">2. Process an Image</h3>
                <div className="bg-gray-900 rounded-lg p-4 relative">
                  <button
                    onClick={() => copyToClipboard(codeExamples['python-sdk'], 'python-quickstart')}
                    className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    {copiedCode === 'python-quickstart' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <pre className="text-green-400 text-sm overflow-x-auto">
                    <code>{codeExamples['python-sdk']}</code>
                  </pre>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">3. View Results</h3>
                <p className="text-gray-600">
                  The API returns detection results with bounding boxes, confidence scores, and class labels.
                </p>
              </div>
            </div>
          </div>
        )

      case 'endpoints':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">API Endpoints</h2>
            <p className="text-gray-600">
              Complete reference for all available API endpoints and their parameters.
            </p>

            <div className="space-y-6">
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">GET</span>
                  <code className="text-lg font-mono">/api/models</code>
                </div>
                <p className="text-gray-600 mb-4">Retrieve a list of all available models.</p>
                <div className="bg-gray-50 rounded p-3">
                  <code className="text-sm">curl -H "Authorization: Bearer YOUR_API_KEY" https://api.autonomouslabs.com/api/models</code>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">POST</span>
                  <code className="text-lg font-mono">/api/infer/image</code>
                </div>
                <p className="text-gray-600 mb-4">Process an image for object detection or segmentation.</p>
                <div className="bg-gray-50 rounded p-3">
                  <code className="text-sm">curl -X POST -F "file=@image.jpg" -F "model_id=yolov8n" -H "Authorization: Bearer YOUR_API_KEY" https://api.autonomouslabs.com/api/infer/image</code>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">POST</span>
                  <code className="text-lg font-mono">/api/infer/video</code>
                </div>
                <p className="text-gray-600 mb-4">Process a video for object detection or segmentation.</p>
                <div className="bg-gray-50 rounded p-3">
                  <code className="text-sm">curl -X POST -F "file=@video.mp4" -F "model_id=deeplabv3" -H "Authorization: Bearer YOUR_API_KEY" https://api.autonomouslabs.com/api/infer/video</code>
                </div>
              </div>
            </div>
          </div>
        )

      case 'python-sdk':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Python SDK</h2>
            <p className="text-gray-600">
              Complete Python SDK documentation with examples and best practices.
            </p>

            <div className="bg-gray-900 rounded-lg p-4 relative">
              <button
                onClick={() => copyToClipboard(codeExamples['python-sdk'], 'python-sdk')}
                className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
              >
                {copiedCode === 'python-sdk' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="text-green-400 text-sm overflow-x-auto">
                <code>{codeExamples['python-sdk']}</code>
              </pre>
            </div>
          </div>
        )

      case 'javascript-sdk':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">JavaScript SDK</h2>
            <p className="text-gray-600">
              Complete JavaScript SDK documentation with examples and best practices.
            </p>

            <div className="bg-gray-900 rounded-lg p-4 relative">
              <button
                onClick={() => copyToClipboard(codeExamples['javascript-sdk'], 'javascript-sdk')}
                className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
              >
                {copiedCode === 'javascript-sdk' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="text-green-400 text-sm overflow-x-auto">
                <code>{codeExamples['javascript-sdk']}</code>
              </pre>
            </div>
          </div>
        )

      case 'docker':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Docker Deployment</h2>
            <p className="text-gray-600">
              Deploy Autonomous Labs using Docker and Docker Compose for easy setup and scaling.
            </p>

            <div className="bg-gray-900 rounded-lg p-4 relative">
              <button
                onClick={() => copyToClipboard(codeExamples['docker'], 'docker')}
                className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white transition-colors"
              >
                {copiedCode === 'docker' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="text-green-400 text-sm overflow-x-auto">
                <code>{codeExamples['docker']}</code>
              </pre>
            </div>
          </div>
        )

      default:
        return (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Topic</h3>
            <p className="text-gray-500">Choose a section from the sidebar to view documentation.</p>
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Developer Documentation
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to integrate Autonomous Labs into your applications
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon
                return (
                  <div key={section.id}>
                    <button
                      onClick={() => {
                        setActiveSection(section.id)
                        setActiveSubsection(section.subsections[0].id)
                      }}
                      className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                        activeSection === section.id
                          ? 'bg-primary-100 text-primary-700 border border-primary-200'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {section.title}
                    </button>
                    {activeSection === section.id && (
                      <div className="ml-8 mt-2 space-y-1">
                        {section.subsections.map((subsection) => (
                          <button
                            key={subsection.id}
                            onClick={() => setActiveSubsection(subsection.id)}
                            className={`block w-full px-4 py-2 text-left text-sm rounded-lg transition-colors ${
                              activeSubsection === subsection.id
                                ? 'bg-primary-50 text-primary-700'
                                : 'text-gray-600 hover:bg-gray-50'
                            }`}
                          >
                            {subsection.title}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
