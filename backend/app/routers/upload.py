import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..auth import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter()

# Directory for uploads - absolute path based on project structure
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")

# Ensure directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Max upload size: 5MB
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

@router.post("/", tags=["Upload"])
async def upload_image(
    file: UploadFile = File(...),
    _admin: str = Depends(get_current_admin)
):
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Только изображения разрешены")

    # Generate unique filename
    ext = os.path.splitext(file.filename or "image.jpg")[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        # Read in chunks to enforce size limit
        total_size = 0
        chunks = []
        while True:
            chunk = await file.read(64 * 1024)  # 64KB chunks
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Файл слишком большой. Максимум {MAX_UPLOAD_SIZE // (1024*1024)}MB"
                )
            chunks.append(chunk)
        
        with open(file_path, "wb") as buffer:
            for chunk in chunks:
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

    # Return the URL. Since backend serves static files from /static, the URL will be:
    return {"url": f"/static/uploads/{filename}"}
