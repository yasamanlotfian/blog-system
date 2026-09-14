

import os

from PIL import Image
from sqlalchemy.orm import Session

from database import SessionLocal
from tables.file import File
from services.image_crop import crop_image


UPLOAD_WEBP_DIR = "static/gallery/webp"
UPLOAD_CROP_DIR = "static/gallery/crop"


os.makedirs(
    UPLOAD_WEBP_DIR,
    exist_ok=True,
)

os.makedirs(
    UPLOAD_CROP_DIR,
    exist_ok=True,
)


def process_image(
    file_path: str,
    file_id: int,
):
    """
    Background task for image processing.

    1. Create WebP
    2. Create crop
    3. Update File record
    """

    db: Session = SessionLocal()

    try:

        
        file_record = (
            db.query(File)
            .filter(File.id == file_id)
            .first()
        )

        if not file_record:
            print(
                f"FILE NOT FOUND: {file_id}"
            )
            return

        image = Image.open(file_path)

        rgb_image = image.convert("RGB")

     
        webp_filename = f"{file_id}.webp"

        webp_path = os.path.join(
            UPLOAD_WEBP_DIR,
            webp_filename,
        )

        rgb_image.save(
            webp_path,
            "WEBP",
            quality=80,
        )


        crop_filename = f"{file_id}.webp"

        crop_path = os.path.join(
            UPLOAD_CROP_DIR,
            crop_filename,
        )

        crop_image(
            rgb_image,
            crop_path,
        )


        file_record.optimized_image_url = (
            f"/static/gallery/webp/{webp_filename}"
        )

        file_record.crop_image_url = (
            f"/static/gallery/crop/{crop_filename}"
        )

        file_record.optimized_file_size = (
            os.path.getsize(webp_path)
        )

        db.commit()

        print(
            f"IMAGE PROCESSING COMPLETED: {file_id}"
        )

    except Exception as e:

        db.rollback()

        print(
            f"IMAGE PROCESSING ERROR: {e}"
        )

    finally:

        db.close()