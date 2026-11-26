"""Input validation: make sure the uploaded image is usable before inference."""

from PIL import Image

from src.config import MAX_IMAGE_SIDE, MIN_IMAGE_SIDE


class InvalidImageError(ValueError):
    """Raised when the user's input cannot be used as an image."""


def validate_image(image) -> Image.Image:
    """Check an uploaded image and return a clean RGB PIL image.

    Raises InvalidImageError with a user-friendly message if the input is
    missing, is not an image, or is too small.
    """
    if image is None:
        raise InvalidImageError("No image provided. Please upload a photo of the waste item.")

    if not isinstance(image, Image.Image):
        raise InvalidImageError("The input is not a valid image. Please upload a JPG or PNG file.")

    width, height = image.size
    if width < MIN_IMAGE_SIDE or height < MIN_IMAGE_SIDE:
        raise InvalidImageError(
            f"The image is too small ({width}x{height}px). "
            f"Please upload an image at least {MIN_IMAGE_SIDE}x{MIN_IMAGE_SIDE}px."
        )

    # Models expect 3 colour channels. PNGs may have transparency (RGBA) and
    # some photos are greyscale ("L"), so convert everything to RGB.
    if image.mode != "RGB":
        if image.mode in ("RGBA", "LA", "P"):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.split()[-1])
            image = background
        else:
            image = image.convert("RGB")

    # Shrink huge photos so inference stays fast (the model resizes anyway).
    if max(image.size) > MAX_IMAGE_SIDE:
        image = image.copy()
        image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))

    return image
