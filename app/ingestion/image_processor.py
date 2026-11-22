from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError


class ImageProcessingError(RuntimeError):
    pass


def load_image(path: Path, max_edge: int = 5000, max_pixels: int = 18_000_000) -> Image.Image:
    try:
        with Image.open(path) as source:
            if source.width * source.height > max_pixels:
                raise ImageProcessingError(
                    f"Image dimensions are too large ({source.width}x{source.height}). "
                    f"Maximum decoded pixels: {max_pixels:,}."
                )
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageProcessingError(f"Unable to read image: {exc}") from exc
    if max(image.size) > max_edge:
        ratio = max_edge / max(image.size)
        image = image.resize((max(1, int(image.width * ratio)), max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
    return image
