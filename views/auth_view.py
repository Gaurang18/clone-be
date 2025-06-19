from supabase import create_client
from config.settings import settings
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from dto.user import UserCreate, UserOut, Token

supabase = create_client(settings.supabase_url, settings.supabase_key)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def signup(email: str, password: str):
    """Handle user signup logic"""
    response = supabase.auth.sign_up({"email": email, "password": password})
    if response.user:
        # Create user profile in Supabase or your preferred storage
        user_data = {
            "id": response.user.id,
            "email": email,
            "tier": "starter",
            "image_credits": 10,
            "download_credits": 5
        }
        return user_data
    else:
        raise HTTPException(status_code=400, detail=response.error.message)

def login(email: str, password: str):
    """Handle user login logic"""
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if response.session:
        return response.session
    else:
        raise HTTPException(status_code=400, detail=response.error.message)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    res = supabase.auth.api.get_user(token)
    if not res.user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # Get user data from your storage (Supabase, etc.)
    user_data = {
        "id": res.user.id,
        "email": res.user.email,
        "tier": "starter",  # Get from storage
        "image_credits": 10,  # Get from storage
        "download_credits": 5  # Get from storage
    }
    return user_data

def resend_verification(email: str):
    """Resend verification email"""
    response = supabase.auth.resend({"email": email, "type": "signup"})
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Verification email resent."}

def forgot_password(email: str):
    """Handle forgot password"""
    response = supabase.auth.reset_password_for_email(email)
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Password reset email sent."} 