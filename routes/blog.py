from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.dependencies import permission_required
from database import get_db

from tables.user import User
from tables.blog import Blog
from tables.category import Category
from tables.tag import Tag

from schemas.blog import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
)


router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
)


def validate_pagination(
    page: int,
    size: int,
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0",
        )

    if size < 1:
        raise HTTPException(
            status_code=400,
            detail="Size must be greater than 0",
        )

    if size > 10:
        raise HTTPException(
            status_code=400,
            detail="Size cannot be greater than 10",
        )


def get_sort_column(
    sort_by: str,
):
    sort_by = sort_by.strip().lower()

    allowed_sort_fields = {
        "id": Blog.id,
        "title": Blog.title,
        "seo_title": Blog.seo_title,
        "slug": Blog.slug,
        "view_num": Blog.view_num,
        "created_at": Blog.created_at,
        "updated_at": Blog.updated_at,
    }

    column = allowed_sort_fields.get(sort_by)

    if column is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. "
                "Allowed values: "
                "id, title, seo_title, slug, "
                "view_num, created_at, updated_at"
            ),
        )

    return column


def get_order_column(
    column,
    sort_order: str,
):
    sort_order = sort_order.strip().lower()

    if sort_order == "asc":
        return column.asc()

    if sort_order == "desc":
        return column.desc()

    raise HTTPException(
        status_code=400,
        detail="sort_order must be 'asc' or 'desc'",
    )



def blog_to_dict(
    blog: Blog,
):
    return {
        "id": blog.id,

        "title": blog.title,

        "slug": blog.slug,

        "seo_title": blog.seo_title,

        "description": blog.description,

        "content": blog.content,

        "view_num": blog.view_num,

        "category_id": blog.category_id,

        "created_at": blog.created_at,

        "updated_at": blog.updated_at,

        "category": (
            {
                "id": blog.category.id,
                "name": blog.category.name,
            }
            if blog.category
            else None
        ),

        "tags": [
            {
                "id": tag.id,
                "name": tag.name,
            }
            for tag in blog.tags
        ],
    }


def blog_detail_to_dict(
    blog: Blog,
):
    data = blog_to_dict(blog)

    data["gallery"] = [
        {
            "id": gallery.id,

            "title": gallery.title,

            "original_image_url":
                gallery.original_image_url,

            "optimized_image_url":
                gallery.optimized_image_url,

            "alt_text":
                gallery.alt_text,

            "original_file_size":
                gallery.original_file_size,

            "optimized_file_size":
                gallery.optimized_file_size,

            "mime_type":
                gallery.mime_type,

            "blog_id":
                gallery.blog_id,
        }

        for gallery in blog.galleries
    ]

    return data


def apply_blog_search(
    query,
    search: str | None,
):
    if not search:
        return query

    search = search.strip()

    if not search:
        return query

    search_text = f"%{search}%"

    return query.filter(
        Blog.tags.any(
            Tag.name.ilike(search_text)
        )
    )




@router.get("/")
def get_blogs(

    page: int = 1,

    size: int = 5,

    search: str | None = None,

    sort_by: str = "id",

    sort_order: str = "desc",

    db: Session = Depends(get_db),
):

    validate_pagination(
        page,
        size,
    )

    column = get_sort_column(
        sort_by
    )

    order_column = get_order_column(
        column,
        sort_order,
    )

    query = db.query(Blog)

    query = apply_blog_search(
        query,
        search,
    )

    total = query.count()

    blogs = (
        query
        .order_by(order_column)
        .offset(
            (page - 1) * size
        )
        .limit(size)
        .all()
    )

    return {
        "page": page,

        "size": size,

        "total": total,

        "data": [
            blog_to_dict(blog)
            for blog in blogs
        ],
    }



@router.get("/{slug}")
def get_blog(

    slug: str,

    page: int = 1,

    size: int = 5,

    search: str | None = None,

    sort_by: str = "id",

    sort_order: str = "desc",

    db: Session = Depends(get_db),
):

    validate_pagination(
        page,
        size,
    )

    blog = (
        db.query(Blog)
        .filter(
            Blog.slug == slug
        )
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found",
        )

 

    now = datetime.now(
        timezone.utc
    )

    if (
        blog.last_view_at is None
        or
        now - blog.last_view_at
        >= timedelta(minutes=1)
    ):

        blog.view_num += 1

        blog.last_view_at = now

        db.commit()

        db.refresh(blog)

 

    column = get_sort_column(
        sort_by
    )

    order_column = get_order_column(
        column,
        sort_order,
    )

 

    similar_query = (
        db.query(Blog)
        .filter(
            Blog.id != blog.id
        )
    )

    if blog.category_id is not None:

        similar_query = (
            similar_query
            .filter(
                Blog.category_id
                == blog.category_id
            )
        )

    similar_query = apply_blog_search(
        similar_query,
        search,
    )

    similar_total = (
        similar_query.count()
    )

    similar_blogs = (
        similar_query
        .order_by(order_column)
        .offset(
            (page - 1) * size
        )
        .limit(size)
        .all()
    )



    return {

        "blog": blog_detail_to_dict(
            blog
        ),

        "similar_blogs": {

            "page": page,

            "size": size,

            "total": similar_total,

            "data": [
                blog_to_dict(
                    similar_blog
                )
                for similar_blog
                in similar_blogs
            ],
        },
    }



@router.post(
    "/",
    response_model=BlogResponse,
)
def create_blog(

    blog_data: BlogCreate,

    db: Session = Depends(get_db),
        current_user: User = Depends(
        permission_required("blog_create")
    ),
):

    existing_blog = (
        db.query(Blog)
        .filter(
            Blog.slug
            == blog_data.slug
        )
        .first()
    )

    if existing_blog:
        raise HTTPException(
            status_code=400,
            detail="Slug already exists",
        )

    if blog_data.category_id is not None:

        category = (
            db.query(Category)
            .filter(
                Category.id
                == blog_data.category_id
            )
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

    blog = Blog(
        title=blog_data.title,

        slug=blog_data.slug,

        seo_title=blog_data.seo_title,

        description=blog_data.description,

        content=blog_data.content,

        category_id=blog_data.category_id,

        view_num=0,

        last_view_at=None,
    )

    db.add(blog)

    db.flush()

    if blog_data.tag_ids is not None:

        tag_ids = list(
            set(blog_data.tag_ids)
        )

        if tag_ids:

            tags = (
                db.query(Tag)
                .filter(
                    Tag.id.in_(tag_ids)
                )
                .all()
            )

            found_tag_ids = {
                tag.id
                for tag in tags
            }

            missing_tag_ids = (
                set(tag_ids)
                - found_tag_ids
            )

            if missing_tag_ids:

                db.rollback()

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Tags not found: "
                        f"{sorted(missing_tag_ids)}"
                    ),
                )

            blog.tags = tags

    db.commit()

    db.refresh(blog)

    return blog



@router.patch(
    "/{blog_id}",
    response_model=BlogResponse,
)
def update_blog(

    blog_id: int,

    blog_data: BlogUpdate,

    db: Session = Depends(get_db),

        current_user: User = Depends(
        permission_required("blog_update")
    ),
):

    blog = (
        db.query(Blog)
        .filter(
            Blog.id == blog_id
        )
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found",
        )

    if blog_data.title is not None:

        blog.title = (
            blog_data.title
        )

    if blog_data.seo_title is not None:

        blog.seo_title = (
            blog_data.seo_title
        )

    if blog_data.slug is not None:

        existing_blog = (
            db.query(Blog)
            .filter(
                Blog.slug
                == blog_data.slug,

                Blog.id
                != blog.id,
            )
            .first()
        )

        if existing_blog:

            raise HTTPException(
                status_code=400,
                detail="Slug already exists",
            )

        blog.slug = (
            blog_data.slug
        )

    if blog_data.description is not None:

        blog.description = (
            blog_data.description
        )

    if blog_data.content is not None:

        blog.content = (
            blog_data.content
        )

    if blog_data.category_id is not None:

        category = (
            db.query(Category)
            .filter(
                Category.id
                == blog_data.category_id
            )
            .first()
        )

        if not category:

            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        blog.category_id = (
            blog_data.category_id
        )

    if blog_data.tag_ids is not None:

        tag_ids = list(
            set(blog_data.tag_ids)
        )

        if not tag_ids:

            blog.tags = []

        else:

            tags = (
                db.query(Tag)
                .filter(
                    Tag.id.in_(tag_ids)
                )
                .all()
            )

            found_tag_ids = {
                tag.id
                for tag in tags
            }

            missing_tag_ids = (
                set(tag_ids)
                - found_tag_ids
            )

            if missing_tag_ids:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Tags not found: "
                        f"{sorted(missing_tag_ids)}"
                    ),
                )

            blog.tags = tags

    db.commit()

    db.refresh(blog)

    return blog


@router.delete(
    "/{blog_id}",
)
def delete_blog(

    blog_id: int,

    db: Session = Depends(get_db),

        current_user: User = Depends(
        permission_required("blog_delete")
    ),
):

    blog = (
        db.query(Blog)
        .filter(
            Blog.id == blog_id
        )
        .first()
    )

    if not blog:

        raise HTTPException(
            status_code=404,
            detail="Blog not found",
        )

    db.delete(blog)

    db.commit()

    return {
        "message":
        "Blog deleted successfully",
    }