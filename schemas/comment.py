from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CommentBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=[
            "سارا",
            "مریم",
            "نگار"
        ]
    )

    content: str = Field(
        ...,
        min_length=1,
        examples=[
            "مقاله خیلی مفیدی بود.",
            "نکات مراقبت از ناخن خیلی خوب بود.",
            "مطلب مفیدی درباره مراقبت از پوست بود."
        ]
    )


class CommentCreate(CommentBase):

    blog_id: int


class CommentUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=[
            "زهرا"
        ]
    )

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        examples=[
            "مقاله بسیار مفیدی بود."
        ]
    )


class CommentResponse(CommentBase):

    id: int
    blog_id: int

    model_config = ConfigDict(
        from_attributes=True
    )