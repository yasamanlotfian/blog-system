
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=255
    )


class UserLogin(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=255
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    permissions: list[str]

    class Config:
        from_attributes = True