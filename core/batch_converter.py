# core/batch_converter.py
from pathlib import Path
from .converter import convert_image


def batch_convert(input_dir: Path, output_dir: Path, output_format: str, quality: int = 85):
    supported_exts = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
    image_files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts and f.is_file()]

    results = {"success": 0, "failed": [], "total": len(image_files)}

    output_dir.mkdir(exist_ok=True)

    for file in image_files:
        try:
            output_path = output_dir / f"{file.stem}_converted.{output_format}"
            convert_image(file, output_path, output_format, quality)
            results["success"] += 1
        except Exception as e:
            results["failed"].append(f"{file.name}: {str(e)}")

    return results