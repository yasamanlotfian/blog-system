from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse
import os

from database import Base, engine

from tables.blog import Blog
from tables.category import Category
from tables.gallery import Gallery
from tables.comment import Comment
from tables.tag import Tag
from tables.blog_tag import blog_tags
from tables.user import User
from tables.Permission import Permission
from tables.user_permissions import UserPermission
from tables.file import File
from tables.video import Video

from routes import (
    blog,
    gallery,
    comment,
    category,
    tag,
    user,
    permission,
    file,
    video
)

from auth.dependencies import get_current_user
from settings import settings


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hair Salon Blog API",
    description="Blog management API for Hair Salon Booking System",
    version="1.0.0"
)


@app.middleware("http")
async def create_video_directories(
    request: Request,
    call_next
):
    os.makedirs(
        settings.OPTIMIZED_VIDEO_DIR,
        exist_ok=True
    )

    response = await call_next(request)

    return response


def get_protected_video(
    directory: str,
    filename: str,
    media_type: str = "video/mp4",
):
    video_directory = os.path.abspath(directory)

    file_path = os.path.abspath(
        os.path.join(
            video_directory,
            filename
        )
    )

    if not file_path.startswith(
        video_directory + os.sep
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="Video file not found"
        )

    return FileResponse(
        file_path,
        media_type=media_type
    )


@app.get(
    "/uploads/gallery/videos/original/{filename}"
)
def get_original_video(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return get_protected_video(
        "uploads/gallery/videos/original",
        filename,
        "video/mp4",
    )


@app.get(
    "/uploads/gallery/videos3/optimized/{filename}"
)
def get_optimized_video(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return get_protected_video(
        "uploads/gallery/videos3/optimized",
        filename,
        "video/mp4",
    )


@app.get(
    "/uploads/gallery/videos2/optimized/{filename}"
)
def get_optimized_video_v2(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return get_protected_video(
        "uploads/gallery/videos2/optimized",
        filename,
        "video/mp4",
    )


@app.get(
    "/uploads/gallery/videos/crop/{filename}"
)
def get_crop_video(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    return get_protected_video(
        "uploads/gallery/videos/crop",
        filename,
        "video/mp4",
    )


@app.get(
    "/uploads/gallery/videos/hls/{video_id}/{filename:path}"
)
def get_hls_video(
    video_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
):
    hls_directory = os.path.abspath(
        os.path.join(
            "uploads/gallery/videos/hls",
            str(video_id)
        )
    )

    file_path = os.path.abspath(
        os.path.join(
            hls_directory,
            filename
        )
    )

    if not file_path.startswith(
        hls_directory + os.sep
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail="HLS file not found"
        )

    if filename.endswith(".m3u8"):
        media_type = "application/vnd.apple.mpegurl"

    elif filename.endswith(".ts"):
        media_type = "video/mp2t"

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid HLS file"
        )

    return FileResponse(
        file_path,
        media_type=media_type
    )


app.include_router(blog.router)

app.include_router(gallery.router)

app.include_router(comment.router)

app.include_router(category.router)

app.include_router(tag.router)

app.include_router(user.router)

app.include_router(permission.router)

app.include_router(file.router)

app.include_router(video.router)

