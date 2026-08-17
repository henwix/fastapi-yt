from pydantic import BaseModel, EmailStr, Field


class LoginInSchema(BaseModel):
    email: EmailStr
    password: str


class ActivateChannelInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)
    uid: str = Field(min_length=51, max_length=51)


class ResendChannelActivationCodeInSchema(BaseModel):
    email: EmailStr


class SetChannelEmailInSchema(BaseModel):
    new_email: EmailStr


class SetChannelEmailConfirmInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)


class ResetChannelPasswordInSchema(BaseModel):
    email: EmailStr


class ResetChannelPasswordConfirmInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)
    uid: str = Field(min_length=51, max_length=51)
    new_password: str
