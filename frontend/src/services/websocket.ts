import { TelemetryData } from '../types'

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  connect(runId?: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    const url = runId ? `${WS_BASE_URL}/ws/sim/${runId}` : `${WS_BASE_URL}/ws/telemetry`
    
    try {
      this.ws = new WebSocket(url)
      this.setupEventHandlers()
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error)
      this.handleReconnect()
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.notifyListeners('message', data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason)
      this.handleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  subscribe(event: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    
    this.listeners.get(event)!.add(callback)
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback)
    }
  }

  private notifyListeners(event: string, data: any): void {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket listener:', error)
        }
      })
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Singleton instance
export const wsService = new WebSocketService()

// Convenience functions for telemetry
export const subscribeToTelemetry = (callback: (data: TelemetryData) => void) => {
  return wsService.subscribe('message', callback)
}

export const subscribeToSimulation = (runId: string, callback: (data: any) => void) => {
  wsService.connect(runId)
  return wsService.subscribe('message', callback)
}
