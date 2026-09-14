from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=[
            "مراقبت از مو",
            "مانیکور",
            "پاکسازی پوست",
            "آرایش صورت",
            "موهای خشک"
        ]
    )


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=[
            "مراقبت از پوست"
        ]
    )


class TagResponse(TagBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )