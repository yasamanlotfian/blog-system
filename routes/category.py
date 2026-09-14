from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from tables.category import Category

from schemas.categtory import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)


router = APIRouter(
    prefix="/category",
    tags=["Category"],
)


@router.post(
    "/",
    response_model=CategoryResponse,
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
):

    existing_category = (
        db.query(Category)
        .filter(
            Category.name == category_data.name
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists",
        )

    category = Category(
        name=category_data.name,
        content=category_data.content,
    )

    db.add(category)

    db.commit()

    db.refresh(category)

    return category



@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):

    return (
        db.query(Category)
        .order_by(Category.id.asc())
        .all()
    )



@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category



@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )



    if category_data.name is not None:

        existing_category = (
            db.query(Category)
            .filter(
                Category.name == category_data.name,
                Category.id != category_id
            )
            .first()
        )

        if existing_category:

            raise HTTPException(
                status_code=400,
                detail="Another category with this name already exists",
            )

        category.name = category_data.name

 

    if category_data.content is not None:

        category.content = category_data.content

    db.commit()

    db.refresh(category)

    return category



@router.delete(
    "/{category_id}",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:

        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    db.delete(category)

    db.commit()

    return {
        "message": "Category deleted successfully"
    }