from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import permission
from database import Base, engine

from tables.blog import Blog
from tables.category import Category
from tables.gallery import Gallery
from tables.comment import Comment
from tables.tag import Tag
from tables.blog_tag import blog_tags
from  tables.user import User
from tables.Permission import Permission
from tables.user_permissions import UserPermission
from tables.file import File
from tables.video import Video


from routes import blog, gallery, comment, category, tag ,  user, permission ,file ,video


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hair Salon Blog API",
    description="Blog management API for Hair Salon Booking System",
    version="1.0.0"
)


app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
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