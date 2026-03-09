from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.data.models.user import User
from app.services.scraper_service import ScraperService
from app.api.schemas.scraper import (
    ScraperTargetCreate,
    ScraperTargetUpdate,
    ScraperTargetResponse,
    ScraperLogResponse,
    ScraperStatsResponse,
    ScraperTestRequest,
    ScraperTestResponse,
    ScraperRunRequest
)
from datetime import datetime
import asyncio
import subprocess
import os

router = APIRouter()


@router.get("/", response_model=List[ScraperTargetResponse])
def get_all_scrapers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all scraper targets"""
    scrapers = ScraperService.get_all_scrapers(db, skip=skip, limit=limit)
    return scrapers


@router.get("/stats", response_model=ScraperStatsResponse)
def get_scraper_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraper statistics"""
    return ScraperService.get_scraper_stats(db)


@router.get("/logs", response_model=List[ScraperLogResponse])
def get_scraper_logs(
    scraper_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraper logs"""
    logs = ScraperService.get_scraper_logs(db, scraper_id=scraper_id, skip=skip, limit=limit)
    return logs


@router.get("/{scraper_id}", response_model=ScraperTargetResponse)
def get_scraper(
    scraper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraper by ID"""
    scraper = ScraperService.get_scraper_by_id(db, scraper_id)
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )
    return scraper


@router.post("/", response_model=ScraperTargetResponse, status_code=status.HTTP_201_CREATED)
def create_scraper(
    scraper_data: ScraperTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new scraper target"""
    # Check if domain already exists
    existing = ScraperService.get_scraper_by_domain(db, scraper_data.domain)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scraper for domain {scraper_data.domain} already exists"
        )

    scraper = ScraperService.create_scraper(db, scraper_data)
    return scraper


@router.put("/{scraper_id}", response_model=ScraperTargetResponse)
def update_scraper(
    scraper_id: int,
    scraper_data: ScraperTargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update scraper target"""
    # Check if domain is being changed and if it already exists
    if scraper_data.domain:
        existing = ScraperService.get_scraper_by_domain(db, scraper_data.domain)
        if existing and existing.id != scraper_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scraper for domain {scraper_data.domain} already exists"
            )

    scraper = ScraperService.update_scraper(db, scraper_id, scraper_data)
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )
    return scraper


@router.delete("/{scraper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scraper(
    scraper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete scraper target"""
    success = ScraperService.delete_scraper(db, scraper_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )
    return None


@router.patch("/{scraper_id}/toggle", response_model=ScraperTargetResponse)
def toggle_scraper(
    scraper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle scraper enabled status"""
    scraper = ScraperService.toggle_scraper(db, scraper_id)
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )
    return scraper


@router.post("/{scraper_id}/test", response_model=ScraperTestResponse)
async def test_scraper(
    scraper_id: int,
    test_data: ScraperTestRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test scraper configuration"""
    scraper = ScraperService.get_scraper_by_id(db, scraper_id)
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )

    # Use provided test data or scraper's configuration
    if not test_data:
        test_data = ScraperTestRequest(
            url_template=scraper.url_template,
            selectors=scraper.selectors,
            test_page=1
        )

    result = await ScraperService.test_scraper_config(test_data)
    return result


@router.post("/{scraper_id}/run")
async def run_scraper(
    scraper_id: int,
    run_data: ScraperRunRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger scraper run"""
    scraper = ScraperService.get_scraper_by_id(db, scraper_id)
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper with ID {scraper_id} not found"
        )

    if not scraper.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot run disabled scraper"
        )

    # Create log entry
    started_at = datetime.utcnow()
    log = ScraperService.create_log(
        db,
        scraper_id=scraper_id,
        started_at=started_at,
        status="running"
    )

    try:
        # Run scraper in background using subprocess
        # This allows the API to return immediately while scraper runs
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        scraper_script = os.path.join(backend_path, "scraper", "run_scraper.py")

        # Build command
        cmd = ["python3", scraper_script, "--scraper-id", str(scraper_id)]
        if run_data and run_data.max_pages:
            cmd.extend(["--max-pages", str(run_data.max_pages)])
        if run_data and run_data.target_items:
            cmd.extend(["--limit", str(run_data.target_items)])

        # Start process in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=backend_path
        )

        return {
            "success": True,
            "message": f"Scraper started for {scraper.domain}",
            "log_id": log.id,
            "started_at": started_at
        }

    except Exception as e:
        # Update log with error
        log.completed_at = datetime.utcnow()
        log.status = "failed"
        log.error_message = str(e)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scraper: {str(e)}"
        )
