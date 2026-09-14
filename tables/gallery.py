from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class Gallery(Base):

    __tablename__ = "galleries"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=True,
    )

    file_id = Column(
        Integer,
        ForeignKey("files.id"),
        nullable=False,
    )

    alt_text = Column(
        String(255),
        nullable=True,
    )

    file = relationship(
        "File",
        back_populates="galleries",
    )