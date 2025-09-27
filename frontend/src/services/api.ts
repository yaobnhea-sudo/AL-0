import axios, { AxiosResponse } from 'axios'
import { 
  Model, 
  DetectionResult, 
  SegmentationResult, 
  LidarResult, 
  TelemetryData, 
  SimulationRun,
  ApiResponse,
  ModelMetrics,
  Dataset
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Models API
export const modelsApi = {
  // Get all available models
  getModels: async (): Promise<Model[]> => {
    const response: AxiosResponse<ApiResponse<Model[]>> = await api.get('/api/models')
    return response.data.data || []
  },

  // Get model details
  getModel: async (id: string): Promise<Model> => {
    const response: AxiosResponse<ApiResponse<Model>> = await api.get(`/api/models/${id}`)
    if (!response.data.data) {
      throw new Error('Model not found')
    }
    return response.data.data
  },

  // Get model metrics
  getModelMetrics: async (id: string): Promise<ModelMetrics> => {
    const response: AxiosResponse<ApiResponse<ModelMetrics>> = await api.get(`/api/models/${id}/metrics`)
    if (!response.data.data) {
      throw new Error('Model metrics not found')
    }
    return response.data.data
  },
}

// Inference API
export const inferenceApi = {
  // Image inference
  inferImage: async (file: File, modelId: string): Promise<DetectionResult | SegmentationResult> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_id', modelId)

    const response: AxiosResponse<ApiResponse<DetectionResult | SegmentationResult>> = await api.post(
      '/api/infer/image',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    if (!response.data.data) {
      throw new Error('Inference failed')
    }
    return response.data.data
  },

  // Video inference
  inferVideo: async (file: File, modelId: string): Promise<{ jobId: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_id', modelId)

    const response: AxiosResponse<ApiResponse<{ jobId: string }>> = await api.post(
      '/api/infer/video',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    if (!response.data.data) {
      throw new Error('Video inference failed')
    }
    return response.data.data
  },

  // Get video inference result
  getVideoResult: async (jobId: string): Promise<{ status: string; result?: DetectionResult[] }> => {
    const response: AxiosResponse<ApiResponse<{ status: string; result?: DetectionResult[] }>> = 
      await api.get(`/api/infer/video/${jobId}`)
    
    if (!response.data.data) {
      throw new Error('Video result not found')
    }
    return response.data.data
  },
}

// Simulation API
export const simulationApi = {
  // Get all simulation runs
  getRuns: async (): Promise<SimulationRun[]> => {
    const response: AxiosResponse<ApiResponse<SimulationRun[]>> = await api.get('/api/simulations')
    return response.data.data || []
  },

  // Create new simulation run
  createRun: async (config: any): Promise<SimulationRun> => {
    const response: AxiosResponse<ApiResponse<SimulationRun>> = await api.post('/api/simulations', config)
    if (!response.data.data) {
      throw new Error('Failed to create simulation run')
    }
    return response.data.data
  },

  // Start simulation
  startSimulation: async (runId: string): Promise<void> => {
    await api.post(`/api/simulations/${runId}/start`)
  },

  // Stop simulation
  stopSimulation: async (runId: string): Promise<void> => {
    await api.post(`/api/simulations/${runId}/stop`)
  },

  // Pause simulation
  pauseSimulation: async (runId: string): Promise<void> => {
    await api.post(`/api/simulations/${runId}/pause`)
  },
}

// Telemetry API
export const telemetryApi = {
  // Get current telemetry data
  getTelemetry: async (): Promise<TelemetryData> => {
    const response: AxiosResponse<ApiResponse<TelemetryData>> = await api.get('/api/telemetry')
    if (!response.data.data) {
      throw new Error('Telemetry data not available')
    }
    return response.data.data
  },

  // Get historical telemetry data
  getHistoricalTelemetry: async (startTime: string, endTime: string): Promise<TelemetryData[]> => {
    const response: AxiosResponse<ApiResponse<TelemetryData[]>> = await api.get(
      `/api/telemetry/history?start=${startTime}&end=${endTime}`
    )
    return response.data.data || []
  },
}

// Datasets API
export const datasetsApi = {
  // Get all datasets
  getDatasets: async (): Promise<Dataset[]> => {
    const response: AxiosResponse<ApiResponse<Dataset[]>> = await api.get('/api/datasets')
    return response.data.data || []
  },

  // Get dataset details
  getDataset: async (id: string): Promise<Dataset> => {
    const response: AxiosResponse<ApiResponse<Dataset>> = await api.get(`/api/datasets/${id}`)
    if (!response.data.data) {
      throw new Error('Dataset not found')
    }
    return response.data.data
  },
}

export default api
