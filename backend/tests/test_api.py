import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestModelsAPI:
    def test_get_models(self):
        """Test getting list of models"""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_model_not_found(self):
        """Test getting a non-existent model"""
        response = client.get("/api/models/nonexistent")
        assert response.status_code == 404
    
    def test_get_model_metrics(self):
        """Test getting model metrics"""
        # First create a model
        response = client.get("/api/models")
        models = response.json()["data"]
        if models:
            model_id = models[0]["id"]
            response = client.get(f"/api/models/{model_id}/metrics")
            # This might return 404 if no metrics exist, which is fine
            assert response.status_code in [200, 404]


class TestInferenceAPI:
    def test_infer_image_no_file(self):
        """Test image inference without file"""
        response = client.post("/api/infer/image")
        assert response.status_code == 422  # Validation error
    
    def test_infer_video_no_file(self):
        """Test video inference without file"""
        response = client.post("/api/infer/video")
        assert response.status_code == 422  # Validation error
    
    def test_get_video_result_not_found(self):
        """Test getting non-existent video result"""
        response = client.get("/api/infer/video/nonexistent")
        assert response.status_code == 404


class TestTelemetryAPI:
    def test_get_telemetry(self):
        """Test getting current telemetry"""
        response = client.get("/api/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        telemetry = data["data"]
        assert "fps" in telemetry
        assert "latency" in telemetry
        assert "cpu_usage" in telemetry
        assert "gpu_usage" in telemetry
        assert "memory_usage" in telemetry
    
    def test_get_telemetry_history(self):
        """Test getting telemetry history"""
        response = client.get("/api/telemetry/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_telemetry_metrics(self):
        """Test getting telemetry metrics"""
        response = client.get("/api/telemetry/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)


class TestDatasetsAPI:
    def test_get_datasets(self):
        """Test getting list of datasets"""
        response = client.get("/api/datasets")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_dataset_not_found(self):
        """Test getting non-existent dataset"""
        response = client.get("/api/datasets/nonexistent")
        assert response.status_code == 404
    
    def test_get_dataset_types(self):
        """Test getting dataset types"""
        response = client.get("/api/datasets/types")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)


class TestSimulationsAPI:
    def test_get_simulations(self):
        """Test getting list of simulations"""
        response = client.get("/api/simulations")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_create_simulation(self):
        """Test creating a simulation"""
        simulation_data = {
            "name": "Test Simulation",
            "config": {
                "scenario": "highway",
                "weather": "clear",
                "time_of_day": "day",
                "traffic": "medium",
                "models": ["yolov8n"]
            }
        }
        response = client.post("/api/simulations", json=simulation_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["name"] == "Test Simulation"
    
    def test_get_simulation_not_found(self):
        """Test getting non-existent simulation"""
        response = client.get("/api/simulations/nonexistent")
        assert response.status_code == 404


class TestHealthEndpoints:
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Autonomous Labs API"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])
