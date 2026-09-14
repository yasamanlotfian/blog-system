from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )

    permission_id = Column(
        Integer,
        ForeignKey("permissions.id"),
        primary_key=True
    )

    granted_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_permissions"
    )

    permission = relationship(
        "Permission",
        foreign_keys=[permission_id],
        back_populates="user_permissions"
    )

    grantor = relationship(
        "User",
        foreign_keys=[granted_by]
    )