
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
)

from sqlalchemy.orm import Session

from tables.file import File as FileTable
from database import get_db

from services.gallery_service import upload_image
from services.video_service import upload_video


router = APIRouter(
    prefix="/file",
    tags=["File"],
)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    try:

        if not file.content_type:
            raise HTTPException(
                status_code=400,
                detail="File content type is missing",
            )

        if file.content_type.startswith("image/"):

            result = upload_image(file)

            new_file = FileTable(
                original_file_url=result[
                    "original_image_url"
                ],
                optimized_file_url=result[
                    "optimized_image_url"
                ],
                crop_file_url=result.get(
                    "crop_image_url"
                ),
                original_file_size=result[
                    "original_file_size"
                ],
                optimized_file_size=result[
                    "optimized_file_size"
                ],
                crop_file_size=result.get(
                    "crop_file_size"
                ),
                mime_type=result[
                    "mime_type"
                ],
                file_type="image",
            )

        elif file.content_type.startswith("video/"):

            result = upload_video(file)

            new_file = FileTable(
                original_file_url=result[
                    "original_video_url"
                ],
                optimized_file_url=None,
                crop_file_url=None,
                original_file_size=result[
                    "original_file_size"
                ],
                optimized_file_size=None,
                crop_file_size=None,
                mime_type=result[
                    "mime_type"
                ],
                file_type="video",
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="Only image and video files are allowed",
            )

        db.add(new_file)

        db.commit()

        db.refresh(new_file)

        return {
            "message": "File uploaded successfully",
            "file_id": new_file.id,
            "file_type": new_file.file_type,
            "mime_type": new_file.mime_type,
            "original_file_url": new_file.original_file_url,
            "optimized_file_url": new_file.optimized_file_url,
            "original_file_size": new_file.original_file_size,
            "optimized_file_size": new_file.optimized_file_size,
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print(
            "FILE DATABASE ERROR:",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save file",
        )