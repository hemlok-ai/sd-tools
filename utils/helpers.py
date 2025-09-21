# utils/helpers.py
"""
共通ユーティリティ関数
"""

from pathlib import Path


def get_image_files(directory: Path, extensions: set = None) -> list:
    """指定ディレクトリ内の画像ファイルを取得"""
    if extensions is None:
        extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}
    return [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in extensions]


def natural_sort_key(path: Path) -> str:
    """自然順ソート用キー（001, 002...）"""
    name = path.stem
    return ''.join(f"{int(c):08d}" if c.isdigit() else c for c in __split_by_digit(name))


def __split_by_digit(s):
    import re
    return re.split(r'(\d+)', s)


def format_bytes(size: int) -> str:
    """バイト数を可読な単位に変換"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"