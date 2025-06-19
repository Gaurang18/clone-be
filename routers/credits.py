from fastapi import APIRouter, Depends, HTTPException
from dto.credit import CreditUpdate, CreditResponse
from views.auth_view import get_current_user
from views.credit_view import update_credits, get_user_credits

router = APIRouter()

@router.post("/update", response_model=CreditResponse)
def update_credit(req: CreditUpdate, user=Depends(get_current_user)):
    try:
        updated_user = update_credits(user, req.credit_type, req.delta)
        return get_user_credits(updated_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=CreditResponse)
def get_credits(user=Depends(get_current_user)):
    return get_user_credits(user) 