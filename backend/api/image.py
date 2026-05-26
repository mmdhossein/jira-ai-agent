# backend/app/api/images.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.image import Image
from typing import Optional

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve an image by ID.
    
    Args:
        image_id: Image ID
        db: Database session
        
    Returns:
        Image binary data with appropriate content type
    """
    try:
        # Query image from database
        image = db.query(Image).filter(Image.id == image_id).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Determine content type
        content_type = f"image/{image.image_type}"
        
        # Return image as binary response
        return Response(
            content=image.image_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=chart_{image_id}.{image.image_type}",
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")


@router.get("/report/{report_id}")
async def get_report_images(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all images associated with a report.
    
    Args:
        report_id: Report ID
        db: Database session
        
    Returns:
        List of image metadata (without binary data)
    """
    try:
        images = db.query(Image).filter(Image.report_id == report_id).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": img.id,
                    "report_id": img.report_id,
                    "image_type": img.image_type,
                    "created_at": img.created_at.isoformat(),
                    "url": f"/images/{img.id}"
                }
                for img in images
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving images: {str(e)}")


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an image by ID.
    
    Args:
        image_id: Image ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        db.delete(image)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Image {image_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")
