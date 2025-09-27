from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import asyncio
import os
from datetime import datetime

from app.core.database import get_db
from app.services.inference_service import InferenceService
from app.services.model_service import ModelService
from app.schemas.inference import (
    ImageInferenceRequest, 
    ImageInferenceResponse,
    VideoInferenceRequest,
    VideoInferenceResponse,
    InferenceJobResponse
)

router = APIRouter()

# In-memory job storage (in production, use Redis or database)
inference_jobs: Dict[str, Dict[str, Any]] = {}


@router.post("/infer/image", response_model=ImageInferenceResponse)
async def infer_image(
    file: UploadFile = File(...),
    model_id: str = Form(...),
    confidence_threshold: float = Form(0.5),
    db: Session = Depends(get_db)
):
    """Process an image for object detection or segmentation"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        # Get model service
        model_service = ModelService()
        model = await model_service.get_model(db=db, model_id=model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Initialize inference service
        inference_service = InferenceService()
        
        # Process image
        start_time = datetime.now()
        result = await inference_service.process_image(
            file=file,
            model_id=model_id,
            confidence_threshold=confidence_threshold
        )
        end_time = datetime.now()
        
        # Calculate inference time
        inference_time = (end_time - start_time).total_seconds() * 1000
        
        # Add inference time to result
        result.inference_time = inference_time
        result.model = model_id
        
        return ImageInferenceResponse(
            success=True,
            data=result,
            message="Image processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/infer/video", response_model=VideoInferenceResponse)
async def infer_video(
    file: UploadFile = File(...),
    model_id: str = Form(...),
    confidence_threshold: float = Form(0.5),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Process a video for object detection or segmentation (async)"""
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Validate file size (100MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="File size too large (max 100MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        # Get model service
        model_service = ModelService()
        model = await model_service.get_model(db=db, model_id=model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store job info
        inference_jobs[job_id] = {
            "status": "processing",
            "model_id": model_id,
            "file_name": file.filename,
            "file_size": file_size,
            "created_at": datetime.now(),
            "result": None,
            "error": None
        }
        
        # Process video in background
        background_tasks.add_task(
            process_video_background,
            job_id=job_id,
            file=file,
            model_id=model_id,
            confidence_threshold=confidence_threshold
        )
        
        return VideoInferenceResponse(
            success=True,
            job_id=job_id,
            message="Video processing started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infer/video/{job_id}", response_model=InferenceJobResponse)
async def get_video_result(job_id: str):
    """Get the result of a video inference job"""
    try:
        if job_id not in inference_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = inference_jobs[job_id]
        
        return InferenceJobResponse(
            success=True,
            job_id=job_id,
            status=job["status"],
            result=job.get("result"),
            error=job.get("error"),
            created_at=job["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/infer/video/{job_id}")
async def cancel_video_job(job_id: str):
    """Cancel a video inference job"""
    try:
        if job_id not in inference_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = inference_jobs[job_id]
        if job["status"] == "processing":
            job["status"] = "cancelled"
            return {"success": True, "message": "Job cancelled"}
        else:
            return {"success": False, "message": "Job cannot be cancelled"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_video_background(
    job_id: str,
    file: UploadFile,
    model_id: str,
    confidence_threshold: float
):
    """Background task to process video"""
    try:
        # Initialize inference service
        inference_service = InferenceService()
        
        # Process video
        result = await inference_service.process_video(
            file=file,
            model_id=model_id,
            confidence_threshold=confidence_threshold
        )
        
        # Update job status
        inference_jobs[job_id]["status"] = "completed"
        inference_jobs[job_id]["result"] = result
        inference_jobs[job_id]["completed_at"] = datetime.now()
        
    except Exception as e:
        # Update job status with error
        inference_jobs[job_id]["status"] = "failed"
        inference_jobs[job_id]["error"] = str(e)
        inference_jobs[job_id]["failed_at"] = datetime.now()


@router.get("/infer/jobs")
async def list_inference_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """List all inference jobs with optional filtering"""
    try:
        jobs = list(inference_jobs.values())
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job["status"] == status]
        
        # Apply pagination
        total = len(jobs)
        jobs = jobs[offset:offset + limit]
        
        return {
            "success": True,
            "data": jobs,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/infer/jobs/{job_id}")
async def delete_inference_job(job_id: str):
    """Delete an inference job and its results"""
    try:
        if job_id not in inference_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        del inference_jobs[job_id]
        
        return {"success": True, "message": "Job deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
