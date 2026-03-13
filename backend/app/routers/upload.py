import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ...auth import get_current_admin

router = APIRouter()

# Directory for uploads - absolute path based on project structure
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")

# Ensure directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", tags=["Upload"])
async def upload_image(
    file: UploadFile = File(...),
    _admin: str = Depends(get_current_admin)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Только изображения разрешены")

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")

    # Return the URL. Since backend serves static files from /static, the URL will be:
    return {"url": f"/static/uploads/{filename}"}
