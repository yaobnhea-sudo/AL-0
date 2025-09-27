import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import { Home } from './pages/Home'
import { Demos } from './pages/Demos'
import { ModelGallery } from './pages/ModelGallery'
import { DeveloperDocs } from './pages/DeveloperDocs'
import { TelemetryDashboard } from './pages/TelemetryDashboard'
import { DataDatasets } from './pages/DataDatasets'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/demos" element={<Demos />} />
            <Route path="/models" element={<ModelGallery />} />
            <Route path="/docs" element={<DeveloperDocs />} />
            <Route path="/telemetry" element={<TelemetryDashboard />} />
            <Route path="/data" element={<DataDatasets />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App
