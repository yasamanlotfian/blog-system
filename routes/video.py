
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
WATERMARK_IMAGE_DIR = "uploads/gallery/videos/watermark"

os.makedirs(WATERMARK_IMAGE_DIR, exist_ok=True)


router = APIRouter(
    prefix="/video",
    tags=["Video"],
)


def make_file_url(file_path):
    if not file_path:
        return None

    return (
        f"{settings.BASE_URL}/"
        f"{file_path.replace(os.sep, '/')}"
    )


@router.get("/file/{video_id}/{video_type}")
def get_video_file(
    video_id: int,
    video_type: str,
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

    file_path = os.path.abspath(file_path)

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
        media_type=video.mime_type or "video/mp4",
    )


def process_video_background(
    video_id,
    original_video_path,
    watermark_picture_path,
    watermark_text,
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
            original_video_path=original_video_path,
            video_id=video_id,
            watermark_picture_path=watermark_picture_path,
            watermark_text=watermark_text,
        )

        video.crop_video_url = result.get(
            "crop_video_url"
        )

        video.optimized_video_url = result.get(
            "optimized_video_url"
        )

        video.optimized_file_size = result.get(
            "optimized_file_size"
        )

        video.hls_url = result.get(
            "hls_url"
        )

        video.status = "done"

        db.commit()

    except Exception:
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

    original_video_path = file.original_file_url

    if not original_video_path:
        raise HTTPException(
            status_code=404,
            detail="Original video path not found",
        )

    watermark_picture_path = None

    if watermark_picture:
        extension = os.path.splitext(
            watermark_picture.filename
        )[1].lower()

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Invalid watermark image",
            )

        watermark_filename = (
            f"{uuid.uuid4()}{extension}"
        )

        watermark_picture_path = os.path.join(
            WATERMARK_IMAGE_DIR,
            watermark_filename,
        )

        with open(
            watermark_picture_path,
            "wb",
        ) as buffer:
            shutil.copyfileobj(
                watermark_picture.file,
                buffer,
            )

    video = Video(
        title=title,
        file_id=file_id,
        original_video_url=original_video_path,
        optimized_video_url=None,
        crop_video_url=None,
        hls_url=None,
        original_file_size=(
            os.path.getsize(original_video_path)
            if os.path.isfile(original_video_path)
            else None
        ),
        optimized_file_size=None,
        mime_type=file.mime_type,
        is_active=1,
        status="pending",
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    background_tasks.add_task(
        process_video_background,
        video.id,
        original_video_path,
        watermark_picture_path,
        watermark_text,
    )

    return {
        "id": video.id,
        "title": video.title,
        "original_video_url": make_file_url(
            video.original_video_url
        ),
        "optimized_video_url": None,
        "crop_video_url": None,
        "hls_url": None,
        "status": video.status,
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

    result = []

    for video in videos:
        result.append({
            "id": video.id,
            "title": video.title,
            "original_video_url": make_file_url(
                video.original_video_url
            ),
            "optimized_video_url": make_file_url(
                video.optimized_video_url
            ),
            "crop_video_url": make_file_url(
                video.crop_video_url
            ),
            "hls_url": make_file_url(
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
        })

    return result


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
        "original_video_url": make_file_url(
            video.original_video_url
        ),
        "optimized_video_url": make_file_url(
            video.optimized_video_url
        ),
        "crop_video_url": make_file_url(
            video.crop_video_url
        ),
        "hls_url": make_file_url(
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
