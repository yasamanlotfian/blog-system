
import os

from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse

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


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hair Salon Blog API",
    description="Blog management API for Hair Salon Booking System",
    version="1.0.0"
)


@app.get("/uploads/{file_path:path}")
def protected_upload(
    file_path: str,
    current_user: User = Depends(get_current_user)
):

    uploads_dir = os.path.abspath("uploads")

    full_path = os.path.abspath(
        os.path.join(
            uploads_dir,
            file_path
        )
    )

    if not (
        full_path == uploads_dir
        or full_path.startswith(uploads_dir + os.sep)
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    allowed_directories = [
        os.path.abspath(
            "uploads/gallery/videos/original"
        ),
        os.path.abspath(
            "uploads/gallery/videos/crop"
        ),
        os.path.abspath(
            "uploads/gallery/videos/hls"
        ),
        os.path.abspath(
            "uploads/gallery/videos/watermark"
        ),
        os.path.abspath(
            "uploads/gallery/videos2/optimized"
        )
    ]

    is_allowed = any(
        full_path == directory
        or full_path.startswith(directory + os.sep)
        for directory in allowed_directories
    )

    if not is_allowed:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if not os.path.isfile(full_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    allowed_extensions = {
        ".mp4",
        ".m3u8",
        ".ts"
    }

    extension = os.path.splitext(
        full_path
    )[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=403,
            detail="File type not allowed"
        )

    if extension == ".mp4":
        media_type = "video/mp4"

    elif extension == ".m3u8":
        media_type = "application/vnd.apple.mpegurl"

    elif extension == ".ts":
        media_type = "video/mp2t"

    else:
        media_type = "application/octet-stream"

    return FileResponse(
        full_path,
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
