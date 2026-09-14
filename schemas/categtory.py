from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=[
            "مو",
            "ناخن",
            "پوست",
            "میکاپ"
        ]
    )

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        examples=[
            "مقالات و مطالب مربوط به مراقبت، زیبایی و سلامت مو.",
            "مقالات و مطالب مربوط به مراقبت و زیبایی ناخن.",
            "مقالات و مطالب مربوط به مراقبت و سلامت پوست.",
            "مقالات و مطالب مربوط به آرایش و میکاپ."
        ]
    )


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=[
            "ناخن"
        ]
    )

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        examples=[
            "مقالات و مطالب مربوط به مراقبت و زیبایی ناخن."
        ]
    )


class CategoryResponse(CategoryBase):

    id: int

    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )