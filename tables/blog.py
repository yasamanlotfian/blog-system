from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Blog(Base):

    __tablename__ = "blogs"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    slug = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    seo_title = Column(
        String(255),
        nullable=True
    )

    description = Column(
        Text,
        nullable=False
    )

    content = Column(
        Text,
        nullable=True
    )

    view_num = Column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )

    last_view_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    category = relationship(
        "Category",
        back_populates="blogs"
    )

    comments = relationship(
        "Comment",
        back_populates="blog",
        cascade="all, delete-orphan"
    )

    tags = relationship(
        "Tag",
        secondary="blog_tags",
        back_populates="blogs"
    )