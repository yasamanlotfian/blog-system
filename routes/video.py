
import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database import get_db, SessionLocal

from tables.file import File as FileTable
from tables.video import Video
from tables.user import User

from services.video_service import process_video

from auth.dependencies import get_current_user

from settings import settings


HLS_VIDEO_DIR = "uploads/gallery/videos/hls"

WATERMARK_IMAGE_DIR = (
    "uploads/gallery/videos/watermark"
)

os.makedirs(
    WATERMARK_IMAGE_DIR,
    exist_ok=True,
)


router = APIRouter(
    prefix="/video",
    tags=["Video"],
)


def make_file_url(file_path):
    if not file_path:
        return None

    return (
        f"{settings.BASE_URL}/video/file/"
        f"{file_path.replace(os.sep, '/')}"
    )


def make_protected_video_url(
    video_id: int,
    video_type: str,
):
    return (
        f"{settings.BASE_URL}"
        f"/video/file/"
        f"{video_id}/"
        f"{video_type}"
    )


@router.get("/file/{video_id}/{video_type}")
def get_video_file(
    video_id: int,
    video_type: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    if video_type == "original":
        file_path = video.original_video_url

    elif video_type == "optimized":
        file_path = video.optimized_video_url

    elif video_type == "crop":
        file_path = video.crop_video_url

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid video type",
        )

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="Video file not available",
        )

    file_path = os.path.abspath(
        file_path
    )

    allowed_directories = [
        os.path.abspath(
            "uploads/gallery/videos/original"
        ),
        os.path.abspath(
            settings.OPTIMIZED_VIDEO_DIR
        ),
        os.path.abspath(
            "uploads/gallery/videos/crop"
        ),
    ]

    is_allowed = any(
        file_path.startswith(
            directory + os.sep
        )
        or file_path == directory
        for directory in allowed_directories
    )

    if not is_allowed:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="Video file not found",
        )

    return FileResponse(
        file_path,
        media_type=video.mime_type
        or "video/mp4",
    )


def process_video_background(
    video_id: int,
    original_video_path: str,
    watermark_picture_path: str | None,
    watermark_text: str | None,
):
    db = SessionLocal()

    try:
        video = (
            db.query(Video)
            .filter(Video.id == video_id)
            .first()
        )

        if not video:
            return

        video.status = "processing"

        db.commit()

        result = process_video(
            original_video_path,
            video_id,
            watermark_picture_path,
            watermark_text,
        )

        video.crop_video_url = result[
            "crop_video_url"
        ]

        video.optimized_video_url = result[
            "optimized_video_url"
        ]

        video.optimized_file_size = result[
            "optimized_file_size"
        ]

        video.hls_url = result[
            "hls_url"
        ]

        video.status = "done"

        db.commit()

    except Exception as e:

        db.rollback()

        video = (
            db.query(Video)
            .filter(Video.id == video_id)
            .first()
        )

        if video:
            video.status = "failed"
            db.commit()

        print(
            "VIDEO BACKGROUND ERROR:",
            e,
        )

    finally:
        db.close()


@router.post("/")
def create_video(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file_id: int = Form(...),
    watermark_text: str | None = Form(None),
    watermark_picture: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    file = (
        db.query(FileTable)
        .filter(
            FileTable.id == file_id,
            FileTable.file_type == "video",
        )
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="Video file not found",
        )

    if (
        watermark_text is not None
        and not watermark_text.strip()
    ):
        watermark_text = None

    allowed_watermark_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    watermark_picture_path = None

    if watermark_picture is not None:

        if (
            watermark_picture.content_type
            not in allowed_watermark_types
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Watermark picture must be "
                    "PNG, JPEG or WEBP"
                ),
            )

        extension = os.path.splitext(
            watermark_picture.filename or ""
        )[1].lower()

        if extension not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid watermark picture "
                    "extension"
                ),
            )

        watermark_filename = (
            f"{uuid.uuid4()}{extension}"
        )

        watermark_picture_path = os.path.join(
            WATERMARK_IMAGE_DIR,
            watermark_filename,
        )

        try:

            content = (
                watermark_picture.file.read()
            )

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="Empty watermark picture",
                )

            with open(
                watermark_picture_path,
                "wb",
            ) as buffer:
                buffer.write(content)

        except HTTPException:
            raise

        except Exception as e:

            if os.path.exists(
                watermark_picture_path
            ):
                os.remove(
                    watermark_picture_path
                )

            print(
                "WATERMARK PICTURE ERROR:",
                e,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to save watermark picture"
                ),
            )

    if (
        watermark_text is None
        and watermark_picture_path is None
    ):
        watermark_type = "none"

    elif (
        watermark_text is not None
        and watermark_picture_path is None
    ):
        watermark_type = "text"

    elif (
        watermark_text is None
        and watermark_picture_path is not None
    ):
        watermark_type = "picture"

    else:
        watermark_type = "text_and_picture"

    video = Video(
        title=title,
        file_id=file.id,
        original_video_url=file.original_file_url,
        optimized_video_url=None,
        original_file_size=file.original_file_size,
        optimized_file_size=None,
        mime_type=file.mime_type,
        hls_url=None,
        is_active=1,
        status="pending",
    )

    try:

        db.add(video)

        db.commit()

        db.refresh(video)

    except Exception as e:

        db.rollback()

        if (
            watermark_picture_path
            and os.path.exists(
                watermark_picture_path
            )
        ):
            os.remove(
                watermark_picture_path
            )

        print(
            "VIDEO CREATE ERROR:",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create video",
        )

    original_video_path = (
        video.original_video_url
    )

    background_tasks.add_task(
        process_video_background,
        video.id,
        original_video_path,
        watermark_picture_path,
        watermark_text,
    )

    return {
        "message": "Video created successfully",

        "video_id": video.id,

        "title": video.title,

        "file_id": video.file_id,

        "original_video_url":
            make_protected_video_url(
                video.id,
                "original",
            ),

        "optimized_video_url":
            (
                make_protected_video_url(
                    video.id,
                    "optimized",
                )
                if video.optimized_video_url
                else None
            ),

        "hls_url":
            make_file_url(
                video.hls_url
            ),

        "watermark_text":
            watermark_text,

        "watermark_picture":
            make_file_url(
                watermark_picture_path
            ),

        "watermark_type":
            watermark_type,

        "status":
            video.status,

        "is_active":
            video.is_active,
    }


@router.get("/")
def get_videos(
    db: Session = Depends(get_db),
):
    videos = (
        db.query(Video)
        .order_by(Video.id.desc())
        .all()
    )

    return [
        {
            "id": video.id,

            "title": video.title,

            "original_video_url":
                make_protected_video_url(
                    video.id,
                    "original",
                ),

            "optimized_video_url":
                (
                    make_protected_video_url(
                        video.id,
                        "optimized",
                    )
                    if video.optimized_video_url
                    else None
                ),

            "crop_video_url":
                (
                    make_protected_video_url(
                        video.id,
                        "crop",
                    )
                    if video.crop_video_url
                    else None
                ),

            "hls_url":
                make_file_url(
                    video.hls_url
                ),

            "original_file_size":
                video.original_file_size,

            "optimized_file_size":
                video.optimized_file_size,

            "mime_type":
                video.mime_type,

            "is_active":
                video.is_active,

            "status":
                video.status,
        }

        for video in videos
    ]


@router.get("/{video_id}")
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    return {
        "id": video.id,

        "title": video.title,

        "original_video_url":
            make_protected_video_url(
                video.id,
                "original",
            ),

        "optimized_video_url":
            (
                make_protected_video_url(
                    video.id,
                    "optimized",
                )
                if video.optimized_video_url
                else None
            ),

        "crop_video_url":
            (
                make_protected_video_url(
                    video.id,
                    "crop",
                )
                if video.crop_video_url
                else None
            ),

        "hls_url":
            make_file_url(
                video.hls_url
            ),

        "original_file_size":
            video.original_file_size,

        "optimized_file_size":
            video.optimized_file_size,

        "mime_type":
            video.mime_type,

        "is_active":
            video.is_active,

        "status":
            video.status,
    }


@router.patch("/{video_id}")
def update_video(
    video_id: int,
    title: str = Form(...),
    db: Session = Depends(get_db),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    video.title = title

    db.commit()

    db.refresh(video)

    return {
        "message":
            "Video updated successfully",

        "video_id":
            video.id,

        "title":
            video.title,
    }


@router.patch("/{video_id}/status")
def update_video_status(
    video_id: int,
    is_active: int = Form(...),
    db: Session = Depends(get_db),
):
    if is_active not in [0, 1]:
        raise HTTPException(
            status_code=400,
            detail="is_active must be 0 or 1",
        )

    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    video.is_active = is_active

    db.commit()

    db.refresh(video)

    return {
        "message":
            "Video status updated successfully",

        "video_id":
            video.id,

        "is_active":
            video.is_active,
    }


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found",
        )

    original_path = (
        video.original_video_url
    )

    optimized_path = (
        video.optimized_video_url
    )

    crop_path = (
        video.crop_video_url
    )

    hls_path = os.path.join(
        HLS_VIDEO_DIR,
        str(video.id),
    )

    try:

        if (
            original_path
            and os.path.exists(
                original_path
            )
        ):
            os.remove(original_path)

        if (
            optimized_path
            and os.path.exists(
                optimized_path
            )
        ):
            os.remove(optimized_path)

        if (
            crop_path
            and os.path.exists(
                crop_path
            )
        ):
            os.remove(crop_path)

        if os.path.exists(hls_path):
            shutil.rmtree(hls_path)

        file = (
            db.query(FileTable)
            .filter(
                FileTable.id == video.file_id
            )
            .first()
        )

        db.delete(video)

        db.commit()

        if file:
            db.delete(file)

            db.commit()

        return {
            "message":
                "Video deleted successfully",

            "video_id":
                video_id,
        }

    except Exception as e:

        db.rollback()

        print(
            "VIDEO DELETE ERROR:",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete video",
        )
