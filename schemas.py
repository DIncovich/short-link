from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    url: HttpUrl

class URLInfo(BaseModel):
    original_url: str
    short_url: str

    class Config:
        from_attributes = True