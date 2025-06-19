from fastapi import HTTPException
from dto.credit import CreditUpdate, CreditResponse

def update_credits(user: dict, credit_type: str, delta: int) -> dict:
    """Update user credits"""
    if credit_type == "image":
        if user["image_credits"] + delta < 0:
            raise HTTPException(status_code=403, detail="Not enough image credits")
        user["image_credits"] += delta
    elif credit_type == "download":
        if user["download_credits"] + delta < 0:
            raise HTTPException(status_code=403, detail="Not enough download credits")
        user["download_credits"] += delta
    else:
        raise HTTPException(status_code=400, detail="Invalid credit type")
    
    # In real implementation, save to your storage
    # For now, just return updated user data
    return user

def get_user_credits(user: dict) -> CreditResponse:
    """Get user credit information"""
    return CreditResponse(
        image_credits=user["image_credits"],
        download_credits=user["download_credits"]
    )

def check_credit_availability(user: dict, credit_type: str, amount: int = 1) -> bool:
    """Check if user has enough credits"""
    if credit_type == "image":
        return user["image_credits"] >= amount
    elif credit_type == "download":
        return user["download_credits"] >= amount
    return False 