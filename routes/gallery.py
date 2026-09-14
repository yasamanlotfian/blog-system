from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    Query,
)

from sqlalchemy.orm import Session

from database import get_db
from tables.gallery import Gallery
from tables.file import File


router = APIRouter(
    prefix="/gallery",
    tags=["Gallery"],
)


@router.get("/")
def get_gallery(
    db: Session = Depends(get_db),
):
    galleries = (
        db.query(Gallery, File)
        .join(
            File,
            Gallery.file_id == File.id
        )
        .all()
    )

    return [
        {
            "gallery_id": gallery.id,
            "file_id": file.id,
            "original_file_url": file.original_file_url,
            "optimized_file_url": file.optimized_file_url,
            "crop_file_url": file.crop_file_url,
            "alt_text": gallery.alt_text,
        }
        for gallery, file in galleries
    ]

@router.post("/") 
def create_gallery(
    file_id: int = Form(...),
    db: Session = Depends(get_db),
):
    file = (
        db.query(File)
        .filter(
            File.id == file_id
        )
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    existing_gallery = (
        db.query(Gallery)
        .filter(
            Gallery.file_id == file_id
        )
        .first()
    )

    if existing_gallery:
        raise HTTPException(
            status_code=400,
            detail="This file is already in gallery",
        )

    gallery = Gallery(
        file_id=file_id,
    )

    try:
        db.add(gallery)
        db.commit()
        db.refresh(gallery)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create gallery",
        )

    return {
    "gallery_id": gallery.id,
    "file_id": file.id,
    "original_file_url": file.original_file_url,
    "optimized_file_url": file.optimized_file_url,
    "crop_file_url": file.crop_file_url,
}

@router.get("/{gallery_id}")
def get_gallery_by_id(
   gallery_id: int,
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(
            Gallery.id == gallery_id
        )
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    return gallery


@router.patch("/{gallery_id}")
def update_gallery(
    gallery_id: int,
    file_id: int | None = Form(None),
    alt_text: str | None = Form(None),
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(
            Gallery.id == gallery_id
        )
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    if file_id is not None:

        file = (
            db.query(File)
            .filter(
                File.id == file_id
            )
            .first()
        )

        if not file:
            raise HTTPException(
                status_code=404,
                detail="File not found",
            )

        gallery.file_id = file_id


    if alt_text is not None:

        gallery.alt_text = (
            alt_text.strip()
            if alt_text.strip()
            else None
        )

    try:

        db.commit()
        db.refresh(gallery)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update gallery",
        )

    return gallery


@router.delete("/{gallery_id}")
def delete_gallery(
    gallery_id: int,
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(
            Gallery.id == gallery_id
        )
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found",
        )

    try:

        db.delete(gallery)
        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete gallery",
        )

    return {
        "message": "Gallery deleted successfully",
    }