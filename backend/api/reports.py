from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.report import Report
from app.models.image import Image
from app.services.pdf_generator import PDFGenerator
import io
from app.services.chart_generator import ChartGenerator
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{report_id}/pdf")
async def download_pdf(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    images = db.query(Image).filter(Image.report_id == report_id).all()
    pdf_gen = PDFGenerator()
    pdf_bytes = await pdf_gen.generate_report_pdf(report, images)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
    )
# ============================================================================
# Image & Report Endpoints
# ============================================================================

@router.get("/images/{image_id}")
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a chart image by ID.
    """
    
    try:
        image = db.query(Image).filter(Image.id == image_id).first()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        return StreamingResponse(
            io.BytesIO(image.image_data),
            media_type=f"image/{image.image_type}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/chart/generate/{report_id}")
async def get_image(report_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a chart image by ID.
    """
    
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="report not found")
        
        char_gen = ChartGenerator()
        gen_type = report.chart_data.get("chart_plan")
        chart_plan = {"gen_type": gen_type}
        normalized_data = {
        "x": report.chart_data["labels"],
        "y": report.chart_data["values"]
        }
        chart_bytes = await char_gen.generate_chart(chart_plan=chart_plan,
                                                    data=normalized_data )
        # Save image if generated
        if chart_bytes:
            image = Image(
                report_id=report_id,
                image_data=chart_bytes,
                image_type="png"
            )
            db.add(image)
            db.commit()
            db.refresh(image)
        return StreamingResponse(
            io.BytesIO(chart_bytes),
            media_type=f"image/png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



