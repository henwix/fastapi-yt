from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class JWTSchema(BaseModel):
    access: str
    refresh: str
