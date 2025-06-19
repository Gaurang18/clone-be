from fastapi import APIRouter, Depends, HTTPException, Request
from dto.payment import CheckoutSession, SessionResponse
from views.payment_view import create_checkout_session, handle_webhook, get_subscription_plans
from views.auth_view import get_current_user

router = APIRouter()

@router.post("/create-session", response_model=SessionResponse)
def create_session(req: CheckoutSession, user=Depends(get_current_user)):
    try:
        session = create_checkout_session(user["email"], req.new_tier.value)
        return SessionResponse(session_id=session.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    return await handle_webhook(request)

@router.get("/plans")
def get_plans():
    """Get available subscription plans"""
    return get_subscription_plans() 