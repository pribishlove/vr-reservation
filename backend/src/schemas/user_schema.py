from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_subscribed_to_email: bool | None = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_subscribed_to_email: bool

    class Config:
        from_attributes = True
