
import os
import uuid

from fastapi import UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError

from services.image_crop import crop_image


UPLOAD_ORIGINAL_DIR = "uploads/gallery/original"
UPLOAD_WEBP_DIR = "uploads/gallery/webp"
UPLOAD_CROP_DIR = "uploads/gallery/crop"


os.makedirs(
    UPLOAD_ORIGINAL_DIR,
    exist_ok=True,
)

os.makedirs(
    UPLOAD_WEBP_DIR,
    exist_ok=True,
)

os.makedirs(
    UPLOAD_CROP_DIR,
    exist_ok=True,
)



ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}



def remove_file(path: str | None):

    if path and os.path.exists(path):

        try:
            os.remove(path)

        except OSError:
            pass


def normalize_path(path: str) -> str:

    return path.replace("\\", "/")


def prepare_image(
    image: Image.Image,
) -> Image.Image:

    if image.mode in (
        "RGBA",
        "P",
        "LA",
    ):
        return image.convert("RGB")

    if image.mode != "RGB":
        return image.convert("RGB")

    return image



def upload_image(
    file: UploadFile,
):
    """
    Upload and process image.

    Creates:

    1. Original image
    2. Optimized WebP
    3. Cropped WebP

    Returns information that will
    be stored in the File table.
    """

  

    if file.content_type not in ALLOWED_MIME_TYPES:

        raise HTTPException(
            status_code=400,
            detail="Invalid image MIME type",
        )


   

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Invalid image extension",
        )



    file_id = str(uuid.uuid4())


    original_path = os.path.join(
        UPLOAD_ORIGINAL_DIR,
        f"{file_id}{extension}",
    )


    optimized_path = os.path.join(
        UPLOAD_WEBP_DIR,
        f"{file_id}.webp",
    )


    crop_path = os.path.join(
        UPLOAD_CROP_DIR,
        f"{file_id}.webp",
    )


    try:

    

        file_content = file.file.read()


        if not file_content:

            raise HTTPException(
                status_code=400,
                detail="Empty file",
            )


    
        with open(
            original_path,
            "wb",
        ) as output_file:

            output_file.write(
                file_content
            )


        try:

            image = Image.open(
                original_path
            )

            image.verify()


            image = Image.open(
                original_path
            )

        except (
            UnidentifiedImageError,
            OSError,
        ):

            remove_file(
                original_path
            )

            raise HTTPException(
                status_code=400,
                detail="Invalid image file",
            )


       

        image = prepare_image(
            image
        )


   

        image.save(
            optimized_path,
            "WEBP",
            quality=85,
            optimize=True,
        )



        cropped_image = crop_image(
            image,
            size=800,
        )


        cropped_image.save(
            crop_path,
            "WEBP",
            quality=85,
            optimize=True,
        )

        original_file_size = os.path.getsize(
            original_path
        )

        optimized_file_size = os.path.getsize(
            optimized_path
        )

        crop_file_size = os.path.getsize(
            crop_path
        )


        original_image_url = normalize_path(
            original_path
        )

        optimized_image_url = normalize_path(
            optimized_path
        )

        crop_image_url = normalize_path(
            crop_path
        )



        return {

            "original_image_url":
                original_image_url,

            "optimized_image_url":
                optimized_image_url,

            "crop_image_url":
                crop_image_url,

            "original_file_size":
                original_file_size,

            "optimized_file_size":
                optimized_file_size,

            "crop_file_size":
                crop_file_size,

            "mime_type":
                file.content_type,
        }


    except HTTPException:

        raise


    except Exception as e:


        remove_file(
            original_path
        )

        remove_file(
            optimized_path
        )

        remove_file(
            crop_path
        )


        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}",
        )