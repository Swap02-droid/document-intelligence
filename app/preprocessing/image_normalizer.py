from PIL import Image, ImageOps, ImageEnhance, ImageFilter


def normalize_image(image: Image.Image) -> Image.Image:
    """Conservative normalization: orientation, RGB, mild contrast and no aggressive binarization."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    # Mild contrast can help scans while avoiding destructive thresholding.
    image = ImageEnhance.Contrast(image).enhance(1.08)
    return image


def upscale_crop(image: Image.Image, factor: float = 1.35, max_edge: int = 5000) -> Image.Image:
    width, height = image.size
    factor = min(factor, max_edge / max(width, height))
    if factor <= 1.0:
        return image.copy()
    resized = image.resize((int(width * factor), int(height * factor)), Image.Resampling.LANCZOS)
    return resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
