from pydantic import BaseModel

class CreditUpdate(BaseModel):
    credit_type: str
    delta: int

class CreditResponse(BaseModel):
    image_credits: int
    download_credits: int 