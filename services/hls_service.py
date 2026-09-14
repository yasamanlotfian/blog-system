import os
import subprocess


HLS_DIR = "uploads/gallery/videos/hls"

os.makedirs(HLS_DIR, exist_ok=True)


def convert_mp4_to_hls(
    input_path: str,
    video_id: int,
):
    output_dir = os.path.join(
        HLS_DIR,
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

    command = [
        "ffmpeg",
        "-i",
        input_path,

        "-c:v",
        "libx264",

        "-c:a",
        "aac",

        "-preset",
        "medium",

        "-crf",
        "28",

        "-f",
        "hls",

        "-hls_time",
        "6",

        "-hls_list_size",
        "0",

        "-hls_segment_filename",
        segment_path,

        playlist_path,
    ]

    subprocess.run(
        command,
        check=True,
    )

    return playlist_path