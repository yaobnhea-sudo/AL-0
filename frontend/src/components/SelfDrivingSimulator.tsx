import { Suspense, useState, useRef, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Box, Sphere, Line } from '@react-three/drei'
import { Vector3, Color, BufferGeometry, Float32BufferAttribute } from 'three'
import { Play, Pause, Square, RotateCcw } from 'lucide-react'

// Simulated LIDAR point cloud data
const generatePointCloud = (count: number = 1000) => {
  const points = []
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count
    const radius = 5 + Math.random() * 10
    const height = (Math.random() - 0.5) * 4
    points.push(
      Math.cos(angle) * radius,
      height,
      Math.sin(angle) * radius
    )
  }
  return points
}

// Simulated detection boxes
const generateDetections = () => {
  return [
    { position: [2, 0, 5], size: [1, 1.5, 0.5], color: 'red', label: 'Car' },
    { position: [-3, 0, 8], size: [0.8, 1.2, 0.4], color: 'blue', label: 'Truck' },
    { position: [0, 0, 12], size: [0.3, 1.7, 0.3], color: 'green', label: 'Person' },
  ]
}

// Point cloud component
function PointCloud({ points }: { points: number[] }) {
  const meshRef = useRef<THREE.Points>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.1
    }
  })

  const geometry = new BufferGeometry()
  geometry.setAttribute('position', new Float32BufferAttribute(points, 3))
  
  return (
    <points ref={meshRef} geometry={geometry}>
      <pointsMaterial size={0.05} color="#00ff88" />
    </points>
  )
}

// Detection box component
function DetectionBox({ position, size, color, label }: any) {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.1
    }
  })

  return (
    <group position={position}>
      <Box ref={meshRef} args={size}>
        <meshBasicMaterial color={color} transparent opacity={0.3} />
      </Box>
      <Text
        position={[0, size[1] / 2 + 0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {label}
      </Text>
    </group>
  )
}

// Ground plane
function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
      <planeGeometry args={[50, 50]} />
      <meshBasicMaterial color="#333333" />
    </mesh>
  )
}

// Camera view component
function CameraView() {
  const { camera } = useThree()
  
  useEffect(() => {
    camera.position.set(0, 2, 5)
    camera.lookAt(0, 0, 0)
  }, [camera])

  return null
}

// Main simulator scene
function SimulatorScene() {
  const [pointCloudData] = useState(() => generatePointCloud(2000))
  const [detections] = useState(() => generateDetections())

  return (
    <>
      <CameraView />
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      
      <Ground />
      
      {/* Point cloud */}
      <PointCloud points={pointCloudData} />
      
      {/* Detection boxes */}
      {detections.map((detection, index) => (
        <DetectionBox key={index} {...detection} />
      ))}
      
      {/* Road markers */}
      {Array.from({ length: 20 }, (_, i) => (
        <Box
          key={i}
          position={[0, -0.9, -i * 2]}
          args={[0.2, 0.1, 1]}
        >
          <meshBasicMaterial color="white" />
        </Box>
      ))}
    </>
  )
}

// Control panel component
function ControlPanel({ 
  isPlaying, 
  onPlay, 
  onPause, 
  onStop, 
  onReset 
}: {
  isPlaying: boolean
  onPlay: () => void
  onPause: () => void
  onStop: () => void
  onReset: () => void
}) {
  return (
    <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg">
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        <span className="text-sm font-medium text-gray-700">Simulation Active</span>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={isPlaying ? onPause : onPlay}
          className="flex items-center px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors"
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
        
        <button
          onClick={onStop}
          className="flex items-center px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
        >
          <Square className="w-4 h-4" />
        </button>
        
        <button
          onClick={onReset}
          className="flex items-center px-3 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

// Main simulator component
export function SelfDrivingSimulator() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [fps, setFps] = useState(30)
  const [latency, setLatency] = useState(16.7)

  const handlePlay = () => setIsPlaying(true)
  const handlePause = () => setIsPlaying(false)
  const handleStop = () => {
    setIsPlaying(false)
    // Reset simulation state
  }
  const handleReset = () => {
    setIsPlaying(false)
    // Reset simulation to initial state
  }

  // Simulate FPS and latency updates
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      setFps(prev => Math.max(25, Math.min(60, prev + (Math.random() - 0.5) * 5)))
      setLatency(prev => Math.max(10, Math.min(50, prev + (Math.random() - 0.5) * 10)))
    }, 1000)

    return () => clearInterval(interval)
  }, [isPlaying])

  return (
    <div className="relative w-full h-[600px] bg-gray-900 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [0, 2, 5], fov: 75 }}>
        <Suspense fallback={null}>
          <SimulatorScene />
          <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
        </Suspense>
      </Canvas>
      
      <ControlPanel
        isPlaying={isPlaying}
        onPlay={handlePlay}
        onPause={handlePause}
        onStop={handleStop}
        onReset={handleReset}
      />
      
      {/* Performance metrics */}
      <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">FPS:</span>
            <span className="font-mono text-green-600">{fps.toFixed(1)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Latency:</span>
            <span className="font-mono text-blue-600">{latency.toFixed(1)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className="text-green-600">Live</span>
          </div>
        </div>
      </div>
      
      {/* Instructions */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg max-w-sm">
        <h4 className="font-semibold text-gray-900 mb-2">Controls</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Mouse: Rotate view</li>
          <li>• Scroll: Zoom in/out</li>
          <li>• Right-click + drag: Pan</li>
          <li>• Use controls to play/pause simulation</li>
        </ul>
      </div>
    </div>
  )
}
