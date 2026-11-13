from PIL import Image, ImageStat
import io

def inspect_image(data: bytes):
    with Image.open(io.BytesIO(data)) as image:
        image.verify()
    with Image.open(io.BytesIO(data)) as image:
        width, height = image.size
        variance = ImageStat.Stat(image.convert("L")).var[0]
    return {
        "width": width, "height": height, "pixels": width * height,
        "brightness_variance": round(variance, 2),
        "note": "مؤشرات آلية أولية ولا تثبت أصالة القطعة أو جودة توثيقها العلمي."
    }
