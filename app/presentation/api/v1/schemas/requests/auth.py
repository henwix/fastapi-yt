from pydantic import BaseModel, EmailStr


class LoginInSchema(BaseModel):
    email: EmailStr
    password: str
