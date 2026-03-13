from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de Datos
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    # Seguridad
    JWT_SECRET_KEY: str = "supersecreto"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Datos del Admin para el sembrado (init_db.py)
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Gmail configuración
    GMAIL_USER: str
    GMAIL_PASSWORD: str

    # URLs para correos
    PLATFORM_URL: str = "http://localhost:4321"

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        extra = "allow"

def get_settings():
    return Settings()
    