from fastapi import APIRouter, HTTPException, status
from ..auth import verify_admin, create_access_token
from ..schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    if not verify_admin(data.username, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    token = create_access_token({"sub": data.username})
    return TokenResponse(access_token=token)
