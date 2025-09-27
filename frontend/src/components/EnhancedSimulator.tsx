import { Suspense, useState, useRef, useEffect, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Box, Sphere, Line, Html, useProgress } from '@react-three/drei'
import { Vector3, Color, BufferGeometry, Float32BufferAttribute, Group } from 'three'
import { Play, Pause, Square, RotateCcw, Settings, Maximize2, Minimize2 } from 'lucide-react'

// Enhanced point cloud with realistic LIDAR data
const generateRealisticPointCloud = (count: number = 2000) => {
  const points = []
  const colors = []
  const intensities = []
  
  // Ground points
  for (let i = 0; i < count * 0.3; i++) {
    const angle = (Math.PI * 2 * i) / (count * 0.3)
    const radius = 5 + Math.random() * 15
    const height = -1 + Math.random() * 0.5
    points.push(Math.cos(angle) * radius, height, Math.sin(angle) * radius)
    colors.push(0.2, 0.2, 0.2) // Dark gray for ground
    intensities.push(0.3 + Math.random() * 0.4)
  }
  
  // Object points (cars, buildings, etc.)
  for (let i = 0; i < count * 0.4; i++) {
    const angle = (Math.PI * 2 * i) / (count * 0.4)
    const radius = 3 + Math.random() * 12
    const height = Math.random() * 3
    points.push(Math.cos(angle) * radius, height, Math.sin(angle) * radius)
    colors.push(0.8, 0.8, 0.8) // Light gray for objects
    intensities.push(0.6 + Math.random() * 0.4)
  }
  
  // Vegetation points
  for (let i = 0; i < count * 0.3; i++) {
    const angle = (Math.PI * 2 * i) / (count * 0.3)
    const radius = 8 + Math.random() * 10
    const height = 0.5 + Math.random() * 2
    points.push(Math.cos(angle) * radius, height, Math.sin(angle) * radius)
    colors.push(0.2, 0.6, 0.2) // Green for vegetation
    intensities.push(0.4 + Math.random() * 0.3)
  }
  
  return { points, colors, intensities }
}

// Enhanced detection boxes with confidence visualization
const generateEnhancedDetections = () => {
  return [
    { 
      position: [2, 0, 5], 
      size: [1.8, 1.5, 4.2], 
      color: 'red', 
      label: 'Car', 
      confidence: 0.92,
      classId: 2,
      velocity: [0.5, 0, 0]
    },
    { 
      position: [-3, 0, 8], 
      size: [2.5, 2.2, 8.5], 
      color: 'blue', 
      label: 'Truck', 
      confidence: 0.87,
      classId: 7,
      velocity: [-0.3, 0, 0]
    },
    { 
      position: [0, 0, 12], 
      size: [0.6, 1.8, 0.6], 
      color: 'green', 
      label: 'Pedestrian', 
      confidence: 0.78,
      classId: 0,
      velocity: [0, 0, 0.2]
    },
    { 
      position: [5, 0, 3], 
      size: [1.0, 1.2, 2.0], 
      color: 'orange', 
      label: 'Cyclist', 
      confidence: 0.85,
      classId: 1,
      velocity: [0.8, 0, 0.1]
    }
  ]
}

// Enhanced point cloud component with realistic rendering
function EnhancedPointCloud({ points, colors, intensities }: { 
  points: number[], 
  colors: number[], 
  intensities: number[] 
}) {
  const meshRef = useRef<THREE.Points>(null)
  const [hovered, setHovered] = useState(false)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.05
      meshRef.current.scale.setScalar(hovered ? 1.1 : 1)
    }
  })

  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(points, 3))
    geo.setAttribute('color', new Float32BufferAttribute(colors, 3))
    geo.setAttribute('intensity', new Float32BufferAttribute(intensities, 1))
    return geo
  }, [points, colors, intensities])
  
  return (
    <points 
      ref={meshRef} 
      geometry={geometry}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <pointsMaterial 
        size={0.08} 
        vertexColors 
        transparent 
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  )
}

// Enhanced detection box with confidence visualization
function EnhancedDetectionBox({ detection }: { detection: any }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)
  
  useFrame((state) => {
    if (meshRef.current) {
      // Animate based on confidence
      const scale = 1 + (detection.confidence - 0.5) * 0.2
      meshRef.current.scale.setScalar(scale)
      
      // Move based on velocity
      meshRef.current.position.x += detection.velocity[0] * 0.01
      meshRef.current.position.z += detection.velocity[2] * 0.01
      
      // Bounce animation
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.1
    }
  })

  const confidenceColor = useMemo(() => {
    const intensity = detection.confidence
    return new Color().setHSL(intensity * 0.3, 1, 0.5)
  }, [detection.confidence])

  return (
    <group position={detection.position}>
      {/* Main bounding box */}
      <Box 
        ref={meshRef} 
        args={detection.size}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshBasicMaterial 
          color={confidenceColor} 
          transparent 
          opacity={0.3} 
          wireframe={hovered}
        />
      </Box>
      
      {/* Confidence indicator */}
      <Box args={[detection.size[0], 0.1, detection.size[2]]} position={[0, -detection.size[1]/2 - 0.1, 0]}>
        <meshBasicMaterial 
          color={confidenceColor} 
          transparent 
          opacity={0.8}
        />
      </Box>
      
      {/* Label with confidence */}
      <Text
        position={[0, detection.size[1] / 2 + 0.5, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="black"
      >
        {detection.label} ({(detection.confidence * 100).toFixed(1)}%)
      </Text>
      
      {/* Velocity arrow */}
      <Line
        points={[
          [0, 0, 0],
          [detection.velocity[0] * 2, detection.velocity[1] * 2, detection.velocity[2] * 2]
        ]}
        color="yellow"
        lineWidth={3}
      />
    </group>
  )
}

// Enhanced ground with road markings
function EnhancedGround() {
  const meshRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      // Animate road markings
      meshRef.current.position.z = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  return (
    <group>
      {/* Main ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
        <planeGeometry args={[50, 50]} />
        <meshBasicMaterial color="#2a2a2a" />
      </mesh>
      
      {/* Road markings */}
      {Array.from({ length: 20 }, (_, i) => (
        <Box
          key={i}
          position={[0, -0.9, -i * 2]}
          args={[0.3, 0.1, 1.5]}
        >
          <meshBasicMaterial color="white" />
        </Box>
      ))}
      
      {/* Lane dividers */}
      {Array.from({ length: 10 }, (_, i) => (
        <Box
          key={`divider-${i}`}
          position={[0, -0.95, -i * 4]}
          args={[0.1, 0.05, 0.5]}
        >
          <meshBasicMaterial color="yellow" />
        </Box>
      ))}
    </group>
  )
}

// Loading component
function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div className="text-white text-center">
        <div className="text-lg mb-2">Loading Simulation...</div>
        <div className="w-32 bg-gray-700 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="text-sm mt-1">{Math.round(progress)}%</div>
      </div>
    </Html>
  )
}

// Main enhanced simulator scene
function EnhancedSimulatorScene() {
  const [pointCloudData] = useState(() => generateRealisticPointCloud(3000))
  const [detections] = useState(() => generateEnhancedDetections())
  const [showStats, setShowStats] = useState(true)
  const [cameraMode, setCameraMode] = useState<'free' | 'follow'>('free')
  const followTarget = useRef<Group>(null)

  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />
      <pointLight position={[0, 10, 0]} intensity={0.5} color="#ffffff" />
      
      <EnhancedGround />
      
      {/* Enhanced point cloud */}
      <EnhancedPointCloud 
        points={pointCloudData.points}
        colors={pointCloudData.colors}
        intensities={pointCloudData.intensities}
      />
      
      {/* Enhanced detection boxes */}
      {detections.map((detection, index) => (
        <EnhancedDetectionBox key={index} detection={detection} />
      ))}
      
      {/* Follow target for camera */}
      <group ref={followTarget} position={[0, 2, 5]}>
        <Sphere args={[0.1]} visible={false} />
      </group>
      
      {/* Stats overlay */}
      {showStats && (
        <Html position={[0, 5, 0]}>
          <div className="bg-black bg-opacity-75 text-white p-4 rounded-lg min-w-[300px]">
            <h3 className="text-lg font-bold mb-2">Simulation Stats</h3>
            <div className="space-y-1 text-sm">
              <div>FPS: 60</div>
              <div>Latency: 16.7ms</div>
              <div>Objects: {detections.length}</div>
              <div>Point Cloud: {pointCloudData.points.length / 3} points</div>
              <div>Camera: {cameraMode}</div>
            </div>
          </div>
        </Html>
      )}
    </>
  )
}

// Enhanced control panel
function EnhancedControlPanel({ 
  isPlaying, 
  onPlay, 
  onPause, 
  onStop, 
  onReset,
  onToggleStats,
  onToggleFullscreen,
  isFullscreen
}: {
  isPlaying: boolean
  onPlay: () => void
  onPause: () => void
  onStop: () => void
  onReset: () => void
  onToggleStats: () => void
  onToggleFullscreen: () => void
  isFullscreen: boolean
}) {
  return (
    <div className="absolute top-4 left-4 bg-black bg-opacity-75 backdrop-blur-sm rounded-lg p-4 shadow-lg text-white">
      <div className="flex items-center space-x-2 mb-4">
        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        <span className="text-sm font-medium">Enhanced Simulation Active</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <button
          onClick={isPlaying ? onPause : onPlay}
          className="flex items-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
        >
          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
        
        <button
          onClick={onStop}
          className="flex items-center px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
        >
          <Square className="w-4 h-4" />
        </button>
        
        <button
          onClick={onReset}
          className="flex items-center px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        
        <button
          onClick={onToggleStats}
          className="flex items-center px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md transition-colors"
        >
          <Settings className="w-4 h-4" />
        </button>
        
        <button
          onClick={onToggleFullscreen}
          className="flex items-center px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors"
        >
          {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  )
}

// Main enhanced simulator component
export function EnhancedSimulator() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [showStats, setShowStats] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [fps, setFps] = useState(60)
  const [latency, setLatency] = useState(16.7)
  const containerRef = useRef<HTMLDivElement>(null)

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
  const handleToggleStats = () => setShowStats(!showStats)
  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  // Simulate FPS and latency updates
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      setFps(prev => Math.max(55, Math.min(65, prev + (Math.random() - 0.5) * 2)))
      setLatency(prev => Math.max(12, Math.min(22, prev + (Math.random() - 0.5) * 2)))
    }, 100)

    return () => clearInterval(interval)
  }, [isPlaying])

  return (
    <div 
      ref={containerRef}
      className={`relative w-full ${isFullscreen ? 'h-screen' : 'h-[600px]'} bg-gray-900 rounded-lg overflow-hidden`}
    >
      <Canvas camera={{ position: [0, 2, 5], fov: 75 }}>
        <Suspense fallback={<Loader />}>
          <EnhancedSimulatorScene />
          <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
        </Suspense>
      </Canvas>
      
      <EnhancedControlPanel
        isPlaying={isPlaying}
        onPlay={handlePlay}
        onPause={handlePause}
        onStop={handleStop}
        onReset={handleReset}
        onToggleStats={handleToggleStats}
        onToggleFullscreen={handleToggleFullscreen}
        isFullscreen={isFullscreen}
      />
      
      {/* Enhanced performance metrics */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-75 backdrop-blur-sm rounded-lg p-4 shadow-lg text-white">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-300">FPS:</span>
            <span className="font-mono text-green-400">{fps.toFixed(1)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Latency:</span>
            <span className="font-mono text-blue-400">{latency.toFixed(1)}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Status:</span>
            <span className="text-green-400">Live</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Mode:</span>
            <span className="text-purple-400">Enhanced</span>
          </div>
        </div>
      </div>
      
      {/* Enhanced instructions */}
      <div className="absolute bottom-4 left-4 bg-black bg-opacity-75 backdrop-blur-sm rounded-lg p-4 shadow-lg max-w-sm text-white">
        <h4 className="font-semibold mb-2">Enhanced Controls</h4>
        <ul className="text-sm space-y-1">
          <li>• Mouse: Rotate view</li>
          <li>• Scroll: Zoom in/out</li>
          <li>• Right-click + drag: Pan</li>
          <li>• Hover objects for details</li>
          <li>• Use controls for simulation</li>
          <li>• Click fullscreen for immersive view</li>
        </ul>
      </div>
    </div>
  )
}
