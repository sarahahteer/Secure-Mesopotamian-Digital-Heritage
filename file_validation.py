
from io import BytesIO
from PIL import Image, UnidentifiedImageError


ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_SIZE = 7 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000


def validate_image(file_data):
    if not file_data:
        raise ValueError("الملف فارغ.")

    if len(file_data) > MAX_IMAGE_SIZE:
        raise ValueError("حجم الصورة يتجاوز الحد المسموح (7 MB).")

    try:
        with Image.open(BytesIO(file_data)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError("صيغة الصورة غير مسموح بها.")

            width, height = image.size

            if width <= 0 or height <= 0:
                raise ValueError("أبعاد الصورة غير صالحة.")

            if width * height > MAX_IMAGE_PIXELS:
                raise ValueError("أبعاد الصورة تتجاوز الحد المسموح.")

            image.verify()

        return True

    except (UnidentifiedImageError, OSError):
        raise ValueError("الملف ليس صورة سليمة أو أن الصورة تالفة.")
