# core/comparer.py
from pathlib import Path


def get_valid_images(paths):
    """有効な画像パスのみをフィルタ"""
    valid_exts = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
    return [p for p in paths if p.exists() and p.suffix.lower() in valid_exts]