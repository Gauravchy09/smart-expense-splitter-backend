from typing import Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.services import ocr_service
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/scan", response_model=Any)
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a receipt image to extract data (Amount, Date, Merchant).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    content = await file.read()
    try:
        data = await ocr_service.process_receipt_image(content)
        # Flatten the data structure to match frontend expectations
        return {**data, "success": True}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
