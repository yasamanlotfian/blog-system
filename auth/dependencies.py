from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from database import get_db
from tables.user import User
from auth.jwt import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



def authenticate_user(
    username: str,
    password: str,
    db: Session
):
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        return None

    if not pwd_context.verify(
        password,
        user.password
    ):
        return None

    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )



def admin_required(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )

    return current_user


def admin_or_operator(
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        "admin",
        "operator"
    ]:

        raise HTTPException(
            
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return current_user


def permission_required(permission_name: str):

    def checker(
        current_user: User = Depends(get_current_user)
    ):

        has_permission = any(
            user_permission.permission.name == permission_name
            for user_permission in current_user.user_permissions
        )

        if not has_permission:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_name}"
            )

        return current_user

    return checker