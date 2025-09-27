import { useState, useEffect } from 'react'
import { Activity, Cpu, MemoryStick, Zap, AlertTriangle, CheckCircle, Clock, BarChart3, TrendingUp, Server } from 'lucide-react'

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  gpu_usage?: number
  gpu_memory_usage?: number
  fps: number
  latency: number
  timestamp: string
}

interface PerformanceSummary {
  time_period_hours: number
  data_points: number
  cpu_usage: {
    average: number
    min: number
    max: number
    current: number
  }
  memory_usage: {
    average: number
    min: number
    max: number
    current: number
  }
  latency: {
    average: number
    min: number
    max: number
    current: number
  }
  fps: {
    average: number
    min: number
    max: number
    current: number
  }
}

interface Alert {
  id: string
  type: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  message: string
  timestamp: string
  resolved: boolean
}

export function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [performanceSummary, setPerformanceSummary] = useState<PerformanceSummary | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(1) // hours
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Fetch system health
  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/monitoring/health')
      const data = await response.json()
      if (data.success) {
        setMetrics(data.data)
      }
    } catch (error) {
      console.error('Error fetching system health:', error)
    }
  }

  // Fetch performance summary
  const fetchPerformanceSummary = async () => {
    try {
      const response = await fetch(`/api/monitoring/performance?hours=${timeRange}`)
      const data = await response.json()
      if (data.success) {
        setPerformanceSummary(data.data)
      }
    } catch (error) {
      console.error('Error fetching performance summary:', error)
    }
  }

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/monitoring/alerts')
      const data = await response.json()
      if (data.success) {
        setAlerts(data.data)
      }
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  // Initial data fetch
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      await Promise.all([
        fetchSystemHealth(),
        fetchPerformanceSummary(),
        fetchAlerts()
      ])
      setIsLoading(false)
    }
    fetchData()
  }, [timeRange])

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchSystemHealth()
    }, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  const getStatusColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'text-red-600'
    if (value >= thresholds.warning) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getStatusIcon = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return <AlertTriangle className="w-5 h-5 text-red-600" />
    if (value >= thresholds.warning) return <AlertTriangle className="w-5 h-5 text-yellow-600" />
    return <CheckCircle className="w-5 h-5 text-green-600" />
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'info': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">System Monitoring</h2>
          <p className="text-gray-600">Real-time system performance and health metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value={1}>Last Hour</option>
            <option value={6}>Last 6 Hours</option>
            <option value={24}>Last 24 Hours</option>
            <option value={168}>Last Week</option>
          </select>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              autoRefresh
                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </button>
        </div>
      </div>

      {/* Real-time Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* CPU Usage */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Cpu className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">CPU Usage</span>
              </div>
              {getStatusIcon(metrics.cpu_usage, { warning: 80, critical: 90 })}
            </div>
            <div className="space-y-2">
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold ${getStatusColor(metrics.cpu_usage, { warning: 80, critical: 90 })}`}>
                  {metrics.cpu_usage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    metrics.cpu_usage >= 90 ? 'bg-red-500' : metrics.cpu_usage >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${metrics.cpu_usage}%` }}
                />
              </div>
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <MemoryStick className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-gray-700">Memory Usage</span>
              </div>
              {getStatusIcon(metrics.memory_usage, { warning: 80, critical: 90 })}
            </div>
            <div className="space-y-2">
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold ${getStatusColor(metrics.memory_usage, { warning: 80, critical: 90 })}`}>
                  {metrics.memory_usage.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    metrics.memory_usage >= 90 ? 'bg-red-500' : metrics.memory_usage >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${metrics.memory_usage}%` }}
                />
              </div>
            </div>
          </div>

          {/* FPS */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-medium text-gray-700">FPS</span>
              </div>
              {getStatusIcon(60 - metrics.fps, { warning: 10, critical: 20 })}
            </div>
            <div className="space-y-2">
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold ${getStatusColor(60 - metrics.fps, { warning: 10, critical: 20 })}`}>
                  {metrics.fps.toFixed(1)}
                </span>
                <span className="text-sm text-gray-500">fps</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    metrics.fps < 30 ? 'bg-red-500' : metrics.fps < 45 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${(metrics.fps / 60) * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Latency */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Clock className="w-5 h-5 text-orange-600" />
                <span className="text-sm font-medium text-gray-700">Latency</span>
              </div>
              {getStatusIcon(metrics.latency, { warning: 50, critical: 100 })}
            </div>
            <div className="space-y-2">
              <div className="flex items-baseline space-x-2">
                <span className={`text-2xl font-bold ${getStatusColor(metrics.latency, { warning: 50, critical: 100 })}`}>
                  {metrics.latency.toFixed(1)}
                </span>
                <span className="text-sm text-gray-500">ms</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    metrics.latency > 100 ? 'bg-red-500' : metrics.latency > 50 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((metrics.latency / 200) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Summary */}
      {performanceSummary && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-2 mb-6">
            <BarChart3 className="w-6 h-6 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Performance Summary</h3>
            <span className="text-sm text-gray-500">({performanceSummary.time_period_hours}h period)</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <div className="text-sm text-gray-600">CPU Usage</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Current:</span>
                  <span className="font-medium">{performanceSummary.cpu_usage.current.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Average:</span>
                  <span className="font-medium">{performanceSummary.cpu_usage.average.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Peak:</span>
                  <span className="font-medium">{performanceSummary.cpu_usage.max.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm text-gray-600">Memory Usage</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Current:</span>
                  <span className="font-medium">{performanceSummary.memory_usage.current.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Average:</span>
                  <span className="font-medium">{performanceSummary.memory_usage.average.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Peak:</span>
                  <span className="font-medium">{performanceSummary.memory_usage.max.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm text-gray-600">FPS</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Current:</span>
                  <span className="font-medium">{performanceSummary.fps.current.toFixed(1)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Average:</span>
                  <span className="font-medium">{performanceSummary.fps.average.toFixed(1)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Peak:</span>
                  <span className="font-medium">{performanceSummary.fps.max.toFixed(1)}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm text-gray-600">Latency</div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Current:</span>
                  <span className="font-medium">{performanceSummary.latency.current.toFixed(1)}ms</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Average:</span>
                  <span className="font-medium">{performanceSummary.latency.average.toFixed(1)}ms</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Peak:</span>
                  <span className="font-medium">{performanceSummary.latency.max.toFixed(1)}ms</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-6">
          <Activity className="w-6 h-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
        </div>
        
        {alerts.length > 0 ? (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`flex items-center justify-between p-4 rounded-lg border ${
                  alert.resolved ? 'opacity-60' : ''
                } ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {alert.severity === 'critical' || alert.severity === 'error' ? (
                      <AlertTriangle className="w-5 h-5" />
                    ) : (
                      <CheckCircle className="w-5 h-5" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium">{alert.message}</div>
                    <div className="text-sm opacity-75">
                      {new Date(alert.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    alert.resolved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {alert.resolved ? 'Resolved' : 'Active'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
            <p>No active alerts</p>
            <p className="text-sm">System is running smoothly</p>
          </div>
        )}
      </div>

      {/* Prometheus Metrics Link */}
      <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
        <div className="flex items-center space-x-2 mb-2">
          <Server className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-blue-900">Prometheus Metrics</h3>
        </div>
        <p className="text-blue-700 mb-4">
          Access detailed Prometheus metrics for advanced monitoring and alerting.
        </p>
        <a
          href="http://localhost:8001/metrics"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          View Prometheus Metrics
        </a>
      </div>
    </div>
  )
}
