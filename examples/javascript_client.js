/**
 * Autonomous Labs JavaScript Client Example
 * 
 * This script demonstrates how to use the Autonomous Labs API with JavaScript.
 */

class AutonomousLabsClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        this.headers = {
            'Content-Type': 'application/json'
        };
        
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: this.headers,
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getModels() {
        return await this.request('/api/models');
    }
    
    async getModel(modelId) {
        return await this.request(`/api/models/${modelId}`);
    }
    
    async inferImage(imageFile, modelId, confidenceThreshold = 0.5) {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('model_id', modelId);
        formData.append('confidence_threshold', confidenceThreshold.toString());
        
        const response = await fetch(`${this.baseUrl}/api/infer/image`, {
            method: 'POST',
            headers: {
                'Authorization': this.headers['Authorization']
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async inferVideo(videoFile, modelId, confidenceThreshold = 0.5) {
        const formData = new FormData();
        formData.append('file', videoFile);
        formData.append('model_id', modelId);
        formData.append('confidence_threshold', confidenceThreshold.toString());
        
        const response = await fetch(`${this.baseUrl}/api/infer/video`, {
            method: 'POST',
            headers: {
                'Authorization': this.headers['Authorization']
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getVideoResult(jobId) {
        return await this.request(`/api/infer/video/${jobId}`);
    }
    
    async getTelemetry() {
        return await this.request('/api/telemetry');
    }
    
    async getDatasets() {
        return await this.request('/api/datasets');
    }
    
    async subscribeTelemetry(callback) {
        const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws/telemetry';
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('Connected to telemetry stream');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'telemetry') {
                callback(data.data);
            }
        };
        
        ws.onclose = () => {
            console.log('Disconnected from telemetry stream');
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        return ws;
    }
}

// Example usage
async function example() {
    const client = new AutonomousLabsClient('http://localhost:8000');
    
    try {
        // Get available models
        console.log('Available models:');
        const modelsResponse = await client.getModels();
        modelsResponse.data.forEach(model => {
            console.log(`  - ${model.name} (${model.id}) - ${model.type}`);
        });
        
        // Get current telemetry
        console.log('\nCurrent telemetry:');
        const telemetry = await client.getTelemetry();
        const data = telemetry.data;
        console.log(`  FPS: ${data.fps}`);
        console.log(`  Latency: ${data.latency}ms`);
        console.log(`  CPU Usage: ${data.cpu_usage}%`);
        console.log(`  GPU Usage: ${data.gpu_usage}%`);
        
        // Subscribe to real-time telemetry
        console.log('\nSubscribing to real-time telemetry...');
        const ws = await client.subscribeTelemetry((data) => {
            console.log(`Real-time FPS: ${data.fps}, Latency: ${data.latency}ms`);
        });
        
        // Keep the connection open for 10 seconds
        setTimeout(() => {
            ws.close();
            console.log('Telemetry subscription closed');
        }, 10000);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Run example if this script is executed directly
if (typeof window === 'undefined') {
    // Node.js environment
    const fetch = require('node-fetch');
    const WebSocket = require('ws');
    
    // Make fetch and WebSocket available globally
    global.fetch = fetch;
    global.WebSocket = WebSocket;
    
    example();
} else {
    // Browser environment
    window.AutonomousLabsClient = AutonomousLabsClient;
    window.example = example;
}
