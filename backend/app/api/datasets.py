from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dataset_service import DatasetService
from app.schemas.dataset import (
    DatasetResponse,
    DatasetListResponse,
    DatasetStatsResponse
)

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse)
async def get_datasets(
    dataset_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get list of available datasets"""
    try:
        dataset_service = DatasetService()
        datasets = await dataset_service.get_datasets(
            db=db,
            dataset_type=dataset_type,
            limit=limit,
            offset=offset
        )
        
        return DatasetListResponse(
            success=True,
            data=datasets,
            total=len(datasets)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific dataset"""
    try:
        dataset_service = DatasetService()
        dataset = await dataset_service.get_dataset(
            db=db,
            dataset_id=dataset_id
        )
        
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return DatasetResponse(
            success=True,
            data=dataset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}/stats", response_model=DatasetStatsResponse)
async def get_dataset_stats(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific dataset"""
    try:
        dataset_service = DatasetService()
        stats = await dataset_service.get_dataset_stats(
            db=db,
            dataset_id=dataset_id
        )
        
        if not stats:
            raise HTTPException(status_code=404, detail="Dataset stats not found")
        
        return DatasetStatsResponse(
            success=True,
            data=stats
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/{dataset_id}/download")
async def download_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Initiate download of a dataset"""
    try:
        dataset_service = DatasetService()
        download_info = await dataset_service.initiate_download(
            db=db,
            dataset_id=dataset_id
        )
        
        return {
            "success": True,
            "download_url": download_info["download_url"],
            "expires_at": download_info["expires_at"],
            "message": "Download initiated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/{dataset_id}/samples")
async def get_dataset_samples(
    dataset_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get sample data from a dataset"""
    try:
        dataset_service = DatasetService()
        samples = await dataset_service.get_dataset_samples(
            db=db,
            dataset_id=dataset_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": samples,
            "dataset_id": dataset_id,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/refresh")
async def refresh_datasets(
    db: Session = Depends(get_db)
):
    """Refresh the dataset registry"""
    try:
        dataset_service = DatasetService()
        await dataset_service.refresh_datasets(db=db)
        
        return {
            "success": True,
            "message": "Dataset registry refreshed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/types")
async def get_dataset_types():
    """Get list of available dataset types"""
    try:
        return {
            "success": True,
            "data": [
                {
                    "id": "detection",
                    "name": "Object Detection",
                    "description": "Datasets for object detection tasks"
                },
                {
                    "id": "segmentation",
                    "name": "Segmentation",
                    "description": "Datasets for semantic segmentation tasks"
                },
                {
                    "id": "lidar",
                    "name": "LIDAR",
                    "description": "Datasets with LIDAR point cloud data"
                },
                {
                    "id": "multimodal",
                    "name": "Multimodal",
                    "description": "Datasets with multiple data modalities"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
