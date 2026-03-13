import cloudinary
import cloudinary.uploader
from app.core.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure = True
)

def upload_image(file, folder: str = "general"):
    try:
        upload_result = cloudinary.uploader.upload(file, folder=f"ctech/{folder}")
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None