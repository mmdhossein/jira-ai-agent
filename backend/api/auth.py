from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import SendOTPRequest, VerifyOTPRequest, AuthResponse
from app.services.auth_service import AuthService
from app.utils import jwt_handler

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp")
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    # auth_service = AuthService()
    result =  AuthService.send_otp(request.mobile_number, otp='1234')

    if result["success"]:
        return {"message": "OTP sent", "otp": "1234"}
    raise HTTPException(status_code=400, detail=result["error"])


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    # auth_service = AuthService(db)
    print("------------>", request.otp)
    result =  AuthService.verify_otp(request.mobile, request.otp)

    if result["success"]:
        user = AuthService.get_or_create_user(db, request.mobile)
        user_dict = {"name":user.full_name, "mobile": request.mobile, "id": user.id}
        print(user_dict)
        token = jwt_handler.create_access_token(user_dict)
        return AuthResponse(
            success=True,
            token=token,
            user=user_dict,
            message="Authenticated"
        )
    raise HTTPException(status_code=401, detail=result["error"])
