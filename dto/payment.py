from pydantic import BaseModel
from dto.user import TierEnum

class CheckoutSession(BaseModel):
    new_tier: TierEnum

class SessionResponse(BaseModel):
    session_id: str 