from pydantic import BaseModel


class JWTOutSchema(BaseModel):
    access: str
    refresh: str
