import os
import uuid

import ffmpeg
from fastapi import HTTPException, UploadFile

from settings import settings


UPLOAD_VIDEO_DIR = "uploads/gallery/videos/original"
OPTIMIZED_VIDEO_DIR = settings.OPTIMIZED_VIDEO_DIR
UPLOAD_CROP_DIR = "uploads/gallery/videos/crop"
WATERMARK_VIDEO_DIR = settings.VIDEO_WATERMARK_DIR
HLS_VIDEO_DIR = "uploads/gallery/videos/hls"


os.makedirs(
    UPLOAD_VIDEO_DIR,
    exist_ok=True,
)

os.makedirs(
    OPTIMIZED_VIDEO_DIR,
    exist_ok=True,
)

os.makedirs(
    UPLOAD_CROP_DIR,
    exist_ok=True,
)

os.makedirs(
    WATERMARK_VIDEO_DIR,
    exist_ok=True,
)

os.makedirs(
    HLS_VIDEO_DIR,
    exist_ok=True,
)


ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
}

ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
}


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def upload_video(
    file: UploadFile,
):
    if file.content_type not in ALLOWED_VIDEO_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid video MIME type",
        )

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid extension",
        )

    file_id = str(uuid.uuid4())

    original_video_path = os.path.join(
        UPLOAD_VIDEO_DIR,
        f"{file_id}{extension}",
    )

    try:
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty file",
            )

        with open(
            original_video_path,
            "wb",
        ) as buffer:
            buffer.write(content)

        original_file_size = os.path.getsize(
            original_video_path
        )

        return {
            "file_id": file_id,
            "original_video_path": original_video_path,
            "original_video_url": normalize_path(
                original_video_path
            ),
            "original_file_size": original_file_size,
            "optimized_video_url": None,
            "optimized_file_size": None,
            "watermarked_video_url": None,
            "watermarked_file_size": None,
            "hls_url": None,
            "mime_type": "video/mp4",
            "file_type": "video",
            "status": "pending",
        }

    except HTTPException:
        raise

    except Exception as e:

        if os.path.exists(
            original_video_path
        ):
            os.remove(
                original_video_path
            )

        raise HTTPException(
            status_code=500,
            detail=f"Video upload failed: {str(e)}",
        )


def process_video_to_crop(
    original_video_path: str,
    video_id: int,
    x: int,
    y: int,
    width: int,
    height: int,
):
    if x < 0 or y < 0:
        raise Exception(
            "Crop x and y cannot be negative"
        )

    if width <= 0 or height <= 0:
        raise Exception(
            "Crop width and height must be greater than zero"
        )

    crop_filename = (
        f"{video_id}_crop.mp4"
    )

    crop_video_path = os.path.join(
        UPLOAD_CROP_DIR,
        crop_filename,
    )

    try:

        input_video = ffmpeg.input(
            original_video_path
        )

        cropped_video = ffmpeg.crop(
            input_video,
            x,
            y,
            width,
            height,
        )

        (
            ffmpeg
            .output(
                cropped_video,
                crop_video_path,
                vcodec="libx264",
                acodec="aac",
                preset="medium",
                crf=28,
                pix_fmt="yuv420p",
                movflags="+faststart",
            )
            .overwrite_output()
            .run(
                capture_stdout=True,
                capture_stderr=True,
            )
        )

        return normalize_path(
            crop_video_path
        )

    except ffmpeg.Error as e:

        error = (
            e.stderr.decode(
                "utf-8",
                errors="ignore",
            )
            if e.stderr
            else "FFmpeg crop error"
        )

        raise Exception(error)


def process_video_to_optimized(
    crop_video_path: str,
    video_id: int,
):
    filename = (
        f"{video_id}_optimized.mp4"
    )

    optimized_video_path = os.path.join(
        OPTIMIZED_VIDEO_DIR,
        filename,
    )

    try:

        (
            ffmpeg
            .input(crop_video_path)
            .output(
                optimized_video_path,
                vcodec="libx264",
                acodec="aac",
                vf="scale=640:360",
                preset="medium",
                crf=28,
                pix_fmt="yuv420p",
                movflags="+faststart",
            )
            .overwrite_output()
            .run(
                capture_stdout=True,
                capture_stderr=True,
            )
        )

        return normalize_path(
            optimized_video_path
        )

    except ffmpeg.Error as e:

        error = (
            e.stderr.decode(
                "utf-8",
                errors="ignore",
            )
            if e.stderr
            else "FFmpeg optimization error"
        )

        raise Exception(error)


def process_video_to_watermark(
    optimized_video_path: str,
    watermark_picture_path: str | None,
    watermark_text: str | None,
    video_id: int,
):
    filename = (
        f"{video_id}_watermarked.mp4"
    )

    # ویدیوی واترمارک‌شده داخل optimized ذخیره می‌شود
    watermarked_video_path = os.path.join(
        OPTIMIZED_VIDEO_DIR,
        filename,
    )

    try:

        input_video = ffmpeg.input(
            optimized_video_path
        )

        current_video = input_video

        # اضافه کردن تصویر واترمارک
        if watermark_picture_path:

            watermark_image = ffmpeg.input(
                watermark_picture_path,
                loop=1,
            )

            watermark_image = (
                watermark_image.filter(
                    "scale",
                    120,
                    -1,
                )
            )

            current_video = ffmpeg.overlay(
                current_video,
                watermark_image,
                x="W-w-20",
                y="H-h-60",
                shortest=1,
            )

        # اضافه کردن متن واترمارک
        if (
            watermark_text
            and watermark_text.strip()
        ):

            safe_watermark_text = (
                watermark_text
                .replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("'", "\\'")
            )

            current_video = (
                current_video.filter(
                    "drawtext",
                    text=safe_watermark_text,
                    fontfile="C:/Windows/Fonts/arial.ttf",
                    fontsize=24,
                    fontcolor="white@0.7",
                    x="w-tw-20",
                    y="h-th-20",
                )
            )

        (
            ffmpeg
            .output(
                current_video,
                watermarked_video_path,
                vcodec="libx264",
                acodec="aac",
                preset="medium",
                crf=28,
                pix_fmt="yuv420p",
                movflags="+faststart",
            )
            .overwrite_output()
            .run(
                capture_stdout=True,
                capture_stderr=True,
            )
        )

        return normalize_path(
            watermarked_video_path
        )

    except ffmpeg.Error as e:

        error = (
            e.stderr.decode(
                "utf-8",
                errors="ignore",
            )
            if e.stderr
            else "FFmpeg watermark error"
        )

        raise Exception(error)


def process_video_to_hls(
    watermarked_video_path: str,
    video_id: int,
):
    output_dir = os.path.join(
        HLS_VIDEO_DIR,
        str(video_id),
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    playlist_path = os.path.join(
        output_dir,
        "playlist.m3u8",
    )

    segment_path = os.path.join(
        output_dir,
        "segment_%03d.ts",
    )

    try:

        (
            ffmpeg
            .input(watermarked_video_path)
            .output(
                playlist_path,
                vcodec="libx264",
                acodec="aac",
                preset="medium",
                crf=28,
                pix_fmt="yuv420p",
                format="hls",
                hls_time=6,
                hls_list_size=0,
                hls_playlist_type="vod",
                hls_segment_filename=segment_path,
            )
            .overwrite_output()
            .run(
                capture_stdout=True,
                capture_stderr=True,
            )
        )

        return normalize_path(
            playlist_path
        )

    except ffmpeg.Error as e:

        error = (
            e.stderr.decode(
                "utf-8",
                errors="ignore",
            )
            if e.stderr
            else "FFmpeg HLS error"
        )

        raise Exception(error)


def process_video(
    original_video_path: str,
    video_id: int,
    watermark_picture_path: str | None = None,
    watermark_text: str | None = None,
    x: int = 0,
    y: int = 0,
    width: int = 640,
    height: int = 360,
):
  
    crop_video_path = process_video_to_crop(
        original_video_path,
        video_id,
        x,
        y,
        width,
        height,
    )

    
    optimized_video_path = (
        process_video_to_optimized(
            crop_video_path,
            video_id,
        )
    )

   
    watermarked_video_path = (
        process_video_to_watermark(
            optimized_video_path,
            watermark_picture_path,
            watermark_text,
            video_id,
        )
    )

    hls_url = process_video_to_hls(
        watermarked_video_path,
        video_id,
    )

    optimized_file_size = os.path.getsize(
        optimized_video_path
    )

    watermarked_file_size = os.path.getsize(
        watermarked_video_path
    )

    return {
        "crop_video_url": crop_video_path,

        "optimized_video_url": optimized_video_path,

        "optimized_file_size": optimized_file_size,

        "watermarked_video_url":
            watermarked_video_path,

        "watermarked_file_size":
            watermarked_file_size,

        "hls_url": hls_url,
    }