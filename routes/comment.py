from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.comment import Comment

from schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)

from auth.dependencies import permission_required


router = APIRouter(
    prefix="/comment",
    tags=["Comment"]
)



@router.post(
    "/",
    response_model=CommentResponse,
    dependencies=[
        Depends(permission_required("comment_create"))
    ]
)
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db)
):
    comment = Comment(
        blog_id=comment_data.blog_id,
        user_id=comment_data.user_id,
        name=comment_data.name,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment



@router.get(
    "/",
    response_model=list[CommentResponse],
    dependencies=[
        Depends(permission_required("comment_read"))
    ]
)
def get_comments(
    db: Session = Depends(get_db)
):
    return db.query(Comment).all()



@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    dependencies=[
        Depends(permission_required("comment_read"))
    ]
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return comment




@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
    dependencies=[
        Depends(permission_required("comment_update"))
    ]
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment_data.name is not None:
        comment.name = comment_data.name

    if comment_data.content is not None:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment



@router.delete(
    "/{comment_id}",
    dependencies=[
        Depends(permission_required("comment_delete"))
    ]
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }