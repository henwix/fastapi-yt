from pydantic import BaseModel, EmailStr


class LoginInSchema(BaseModel):
    email: EmailStr
    password: str


class JWTOutSchema(BaseModel):
    access: str
    refresh: str
