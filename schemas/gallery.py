from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class GalleryBase(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=[
            "مراقبت از مو",
            "مراقبت از ناخن",
            "مراقبت از پوست",
            "مراقبت از موهای خشک",
            "آماده‌سازی پوست برای میکاپ",
        ],
    )

    alt_text: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=[
            "مراقبت از موهای خشک",
        ],
    )


class GalleryCreate(GalleryBase):

    image_id: int = Field(
        ...,
        gt=0,
        examples=[
            1,
            2,
            3,
        ],
    )


class GalleryUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    alt_text: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    image_id: Optional[int] = Field(
        default=None,
        gt=0,
    )


class GalleryResponse(GalleryBase):

    id: int

    image_id: int

    original_image_url: str

    optimized_image_url: str

    crop_image_url: Optional[str] = None

    original_file_size: int

    optimized_file_size: int

    crop_file_size: Optional[int] = None

    mime_type: str

    model_config = ConfigDict(
        from_attributes=True,
    )