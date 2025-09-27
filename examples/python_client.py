#!/usr/bin/env python3
"""
Autonomous Labs Python Client Example

This script demonstrates how to use the Autonomous Labs API with Python.
"""

import requests
import json
import time
from typing import Optional, Dict, Any
import argparse


class AutonomousLabsClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        response = self.session.get(f"{self.base_url}/api/models")
        response.raise_for_status()
        return response.json()
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get details of a specific model"""
        response = self.session.get(f"{self.base_url}/api/models/{model_id}")
        response.raise_for_status()
        return response.json()
    
    def infer_image(self, image_path: str, model_id: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Process an image for inference"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'model_id': model_id,
                'confidence_threshold': confidence_threshold
            }
            response = self.session.post(f"{self.base_url}/api/infer/image", files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def infer_video(self, video_path: str, model_id: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Process a video for inference"""
        with open(video_path, 'rb') as f:
            files = {'file': f}
            data = {
                'model_id': model_id,
                'confidence_threshold': confidence_threshold
            }
            response = self.session.post(f"{self.base_url}/api/infer/video", files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def get_video_result(self, job_id: str) -> Dict[str, Any]:
        """Get result of a video inference job"""
        response = self.session.get(f"{self.base_url}/api/infer/video/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get current system telemetry"""
        response = self.session.get(f"{self.base_url}/api/telemetry")
        response.raise_for_status()
        return response.json()
    
    def get_datasets(self) -> Dict[str, Any]:
        """Get list of available datasets"""
        response = self.session.get(f"{self.base_url}/api/datasets")
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="Autonomous Labs Python Client Example")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--image", help="Path to image file for inference")
    parser.add_argument("--video", help="Path to video file for inference")
    parser.add_argument("--model", default="yolov8n", help="Model ID to use")
    parser.add_argument("--confidence", type=float, default=0.5, help="Confidence threshold")
    
    args = parser.parse_args()
    
    # Initialize client
    client = AutonomousLabsClient(base_url=args.url, api_key=args.api_key)
    
    try:
        # Get available models
        print("Available models:")
        models_response = client.get_models()
        for model in models_response.get('data', []):
            print(f"  - {model['name']} ({model['id']}) - {model['type']}")
        
        print()
        
        # Get telemetry
        print("Current telemetry:")
        telemetry = client.get_telemetry()
        data = telemetry.get('data', {})
        print(f"  FPS: {data.get('fps', 'N/A')}")
        print(f"  Latency: {data.get('latency', 'N/A')}ms")
        print(f"  CPU Usage: {data.get('cpu_usage', 'N/A')}%")
        print(f"  GPU Usage: {data.get('gpu_usage', 'N/A')}%")
        
        print()
        
        # Process image if provided
        if args.image:
            print(f"Processing image: {args.image}")
            result = client.infer_image(args.image, args.model, args.confidence)
            
            if result.get('success'):
                data = result.get('data', {})
                boxes = data.get('boxes', [])
                print(f"  Found {len(boxes)} detections:")
                for i, box in enumerate(boxes):
                    print(f"    {i+1}. {box['class_name']} (confidence: {box['confidence']:.2f})")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        # Process video if provided
        if args.video:
            print(f"Processing video: {args.video}")
            result = client.infer_video(args.video, args.model, args.confidence)
            
            if result.get('success'):
                job_id = result.get('job_id')
                print(f"  Video processing started. Job ID: {job_id}")
                
                # Poll for results
                while True:
                    time.sleep(2)
                    job_result = client.get_video_result(job_id)
                    
                    if job_result.get('success'):
                        status = job_result.get('status')
                        print(f"  Status: {status}")
                        
                        if status == 'completed':
                            results = job_result.get('result', [])
                            print(f"  Processing completed. Processed {len(results)} frames.")
                            break
                        elif status == 'failed':
                            print(f"  Processing failed: {job_result.get('error', 'Unknown error')}")
                            break
                    else:
                        print(f"  Error checking job status: {job_result.get('error', 'Unknown error')}")
                        break
        
        # Get datasets
        print("Available datasets:")
        datasets_response = client.get_datasets()
        for dataset in datasets_response.get('data', []):
            print(f"  - {dataset['name']} ({dataset['type']}) - {dataset['samples']} samples")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
