
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from tables.blog_tag import blog_tags


class Tag(Base):

    __tablename__ = "tags"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False ,
        index =True
    )

    blogs = relationship(
        "Blog",
        secondary=blog_tags,
        back_populates="tags"
    )
  