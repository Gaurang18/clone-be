from pydantic import BaseModel
import uuid
from enum import Enum

class TierEnum(str, Enum):
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    tier: TierEnum
    image_credits: int
    download_credits: int

class Token(BaseModel):
    access_token: str
    token_type: str 