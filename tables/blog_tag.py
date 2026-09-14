from sqlalchemy import Table, Column, Integer, ForeignKey

from database import Base


blog_tags = Table(
    "blog_tags",
    Base.metadata,

    Column(
        "blog_id",
        Integer,
        ForeignKey("blogs.id"),
        primary_key=True
    ),

    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id"),
        primary_key=True
    )
)