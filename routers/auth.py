from fastapi import APIRouter, HTTPException, Depends, Body
from dto.user import UserCreate, UserOut, Token
from views.auth_view import signup, login, get_current_user, resend_verification, forgot_password

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup_route(user: UserCreate):
    try:
        user_data = signup(user.email, user.password)
        return UserOut(**user_data)
    except Exception as e:
        # Check for Supabase "already registered" error
        if "already registered" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already registered. Please sign in.")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login_route(user: UserCreate):
    try:
        session = login(user.email, user.password)
        return Token(access_token=session.access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserOut)
def read_users_me(user = Depends(get_current_user)):
    return UserOut(**user)

@router.post("/resend-verification")
def resend_verification_route(email: str = Body(..., embed=True)):
    try:
        return resend_verification(email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forgot-password")
def forgot_password_route(email: str = Body(..., embed=True)):
    try:
        return forgot_password(email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 