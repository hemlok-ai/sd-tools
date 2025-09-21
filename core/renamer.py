# core/renamer.py
from pathlib import Path
import random


def sequential_rename(files: list, prefix: str = "", sort_key: str = "name"):
    """ファイルリストを連番リネーム（生成器）"""
    if sort_key == "name":
        files.sort(key=lambda x: x.name)
    elif sort_key == "size":
        files.sort(key=lambda x: x.stat().st_size)
    elif sort_key == "date":
        files.sort(key=lambda x: x.stat().st_mtime)
    elif sort_key == "random":
        random.shuffle(files)

    for i, file in enumerate(files, 1):
        new_name = f"{prefix}{i:03d}{file.suffix}"
        yield file, file.parent / new_name