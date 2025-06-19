from pydantic import BaseModel
import uuid

class AdOut(BaseModel):
    id: uuid.UUID
    image_url: str
    title: str
    description: str

class KeywordRequest(BaseModel):
    keyword: str

class CloneRequest(BaseModel):
    new_image_url: str
    new_description: str

class ImageResponse(BaseModel):
    image_url: str 