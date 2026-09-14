from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Video(Base):

    __tablename__ = "videos"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    file_id = Column(
        Integer,
        ForeignKey("files.id"),
        nullable=False,
    )

    original_video_url = Column(
        String,
        nullable=False,
    )

    optimized_video_url = Column(
        String,
        nullable=True,
    )

    original_file_size = Column(
        Integer,
        nullable=False,
    )
    
    crop_video_url = Column(
    String,
    nullable=True,
)

    optimized_file_size = Column(
        Integer,
        nullable=True,
    )

    mime_type = Column(
        String,
        nullable=False,
    )

    hls_url = Column(
        String,
        nullable=True,
    )

    is_active = Column(
        Integer,
        default=1,
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
    )

    file = relationship(
        "File",
        back_populates="videos",
    )