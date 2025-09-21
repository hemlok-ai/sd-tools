# core/converter.py
from PIL import Image
from pathlib import Path


def convert_image(input_path: Path, output_path: Path, output_format: str, quality: int = 85):
    """単一画像を変換"""
    format_map = {"png": "PNG", "webp": "WEBP", "jpg": "JPEG"}
    target_format = format_map[output_format]

    with Image.open(input_path) as img:
        # JPGはRGBに変換
        if output_format == "jpg" and img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        save_kwargs = {}
        if output_format in ("webp", "jpg"):
            save_kwargs["quality"] = quality
            if output_format == "jpg":
                save_kwargs["optimize"] = True

        img.save(output_path, format=target_format, **save_kwargs)