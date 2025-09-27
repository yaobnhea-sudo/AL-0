import { MonitoringDashboard } from '../components/MonitoringDashboard'

export function TelemetryDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Telemetry Dashboard</h1>
            <p className="text-gray-600 mt-1">Real-time system performance monitoring and health metrics</p>
          </div>
        </div>
      </div>

      {/* Monitoring Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <MonitoringDashboard />
      </div>
    </div>
  )
}