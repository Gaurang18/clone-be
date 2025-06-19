import stripe
from fastapi import HTTPException
from starlette.requests import Request
from config.settings import settings
from dto.payment import CheckoutSession, SessionResponse

stripe.api_key = settings.stripe_secret_key

# Tier mapping
TIER_MAP = {
    "starter": settings.stripe_price_starter,
    "pro": settings.stripe_price_pro,
    "enterprise": settings.stripe_price_enterprise,
}

def create_checkout_session(email: str, new_tier: str) -> stripe.checkout.Session:
    """Create Stripe checkout session"""
    price_id = TIER_MAP.get(new_tier)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    session = stripe.checkout.Session.create(
        customer_email=email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.domain}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.domain}/cancel",
    )
    return session

async def handle_webhook(request: Request) -> dict:
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        price_id = session["display_items"][0]["price"]["id"]
        
        # Update user tier based on payment
        # In real implementation, update user data in your storage
        user_email = session["customer_email"]
        new_tier = None
        
        for tier, tier_price_id in TIER_MAP.items():
            if tier_price_id == price_id:
                new_tier = tier
                break
        
        if new_tier:
            # Update user tier and credits in your storage
            print(f"Updating user {user_email} to tier {new_tier}")
    
    return {"status": "success"}

def get_subscription_plans() -> dict:
    """Get available subscription plans"""
    return {
        "starter": {
            "name": "Starter",
            "price_id": settings.stripe_price_starter,
            "image_credits": 10,
            "download_credits": 5
        },
        "pro": {
            "name": "Pro",
            "price_id": settings.stripe_price_pro,
            "image_credits": 100,
            "download_credits": 50
        },
        "enterprise": {
            "name": "Enterprise",
            "price_id": settings.stripe_price_enterprise,
            "image_credits": 1000,
            "download_credits": 500
        }
    } 