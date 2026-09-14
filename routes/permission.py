from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.user import User
from tables.Permission import Permission
from tables.user_permissions import UserPermission
from auth.dependencies import admin_required


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@router.post("/users/{user_id}/{permission_id}")
def give_permission(
    user_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
   
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    permission = (
        db.query(Permission)
        .filter(Permission.id == permission_id)
        .first()
    )

    if not permission:
        raise HTTPException(
            status_code=404,
            detail="Permission not found"
        )

   
    existing_permission = (
        db.query(UserPermission)
        .filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id
        )
        .first()
    )

    if existing_permission:
        raise HTTPException(
            status_code=400,
            detail="Permission already assigned"
        )
    
    new_user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission_id,
        granted_by=current_user.id
    )

    db.add(new_user_permission)
    db.commit()
    db.refresh(new_user_permission)

    return {
        "message": "Permission assigned successfully",
        "user_id": user.id,
        "username": user.username,
        "permission": permission.name,
        "granted_by": current_user.username
    }