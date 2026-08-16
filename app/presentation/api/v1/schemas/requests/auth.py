from pydantic import BaseModel, EmailStr, Field


class LoginInSchema(BaseModel):
    email: EmailStr
    password: str


class ActivateChannelInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)
    channel_id: str = Field(min_length=51, max_length=51)
