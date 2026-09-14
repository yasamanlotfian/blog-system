
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from tables.user import User
from schemas.user import UserCreate, UserResponse

from auth.jwt import create_access_token
from auth.dependencies import (
    permission_required
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    
    username_exists = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if username_exists:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    email_exists = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = pwd_context.hash(
        user.password
    )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.username == form.username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not pwd_context.verify(
        form.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role
    }

@router.get(
    "/",
    response_model=list[UserResponse],
    dependencies=[
        Depends(permission_required("user_read"))
    ]
)
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": [
                user_permission.permission.name
                for user_permission in user.user_permissions
            ]
        }
        for user in users
    ]



@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[
        Depends(permission_required("user_create"))
    ]
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check username
    username_exists = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if username_exists:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check email
    email_exists = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Hash password
    hashed_password = pwd_context.hash(
        user.password
    )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[
        Depends(permission_required("user_update"))
    ]
)


def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

   
    username_exists = (
        db.query(User)
        .filter(
            User.username == user.username,
            User.id != user_id
        )
        .first()
    )

    if username_exists:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    email_exists = (
        db.query(User)
        .filter(
            User.email == user.email,
            User.id != user_id
        )
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = pwd_context.hash(
        user.password
    )

    db.commit()
    db.refresh(db_user)

    return db_user



@router.delete(
    "/{user_id}",
    dependencies=[
        Depends(permission_required("user_delete"))
    ]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
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

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }