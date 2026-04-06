from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "viewer"   # optional input

class UserLogin(BaseModel):
    email: str
    password: str