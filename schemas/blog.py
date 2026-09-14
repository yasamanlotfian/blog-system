from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from schemas.categtory import CategoryResponse
from schemas.tag import TagResponse


class BlogBase(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=[
            "نکات مهم برای مراقبت از مو",
            "چگونه از ناخن‌های خود مراقبت کنیم؟",
            "مراقبت از پوست قبل از آرایش",
            "روش‌های مراقبت از موهای خشک",
            "مراحل آماده‌سازی پوست برای میکاپ"
        ]
    )

    seo_title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=[
            "بهترین روش مراقبت از مو",
            "روش‌های مراقبت از ناخن",
            "مراقبت از پوست قبل از میکاپ",
            "بهترین روش مراقبت از موهای خشک", 
           "آماده‌سازی پوست قبل از میکاپ"
        ]
    )

    slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=[
            "hair-care-tips",
            "nail-care-tips",
            "skin-care-before-makeup",
            "dry-hair-care",
            "skin-preparation-for-makeup"
        ]
    )

    description: str = Field(
        ...,
        min_length=1,
        examples=[
            "چند نکته ساده برای داشتن موهایی سالم و زیبا.",
            "نکات ساده برای داشتن ناخن‌های سالم و زیبا.",
            "چند نکته کاربردی برای آماده کردن پوست قبل از آرایش.",
            "روش‌های ساده برای مراقبت و تقویت موهای خشک.",
            "نکات مهم برای آماده کردن پوست قبل از انجام میکاپ."
        ]
    )

    content: Optional[str] = None

    category_id: Optional[int] = Field(
        default=None,
        examples=[1, 2, 3, 4]
    )


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["روش‌های جدید مراقبت از مو"]
    )

    seo_title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["بهترین روش‌های جدید مراقبت از مو"]
    )

    slug: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["new-hair-care-tips"]
    )

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        examples=["روش‌های جدید و کاربردی برای مراقبت از مو."]
    )

    content: Optional[str] = Field(
        default=None,
        examples=["مراقبت صحیح از مو باعث سلامت و زیبایی بیشتر موها می‌شود."]
    )

    category_id: Optional[int] = Field(
        default=None,
        examples=[1]
    )

    tag_ids: Optional[list[int]] = Field(
        default=None,
        examples=[
            [1, 5]
        ]
    )


class BlogResponse(BlogBase):

    id: int

    view_num: int
    summary: Optional[str] = None

    created_at: Optional[datetime] = None
    
    updated_at: Optional[datetime] = None

    category: Optional[CategoryResponse] = None

    tags: list[TagResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )