import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "IT_job_data")
    
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_USER = os.getenv("MINIO_ACCESS_KEY", "ROOT_USER")
    MINIO_PASSWORD = os.getenv("MINIO_SECRET_KEY", "CHANGEME123")
    
    RAW_BUCKET = "raw-zone"
    CLEAN_BUCKET = "clean-zone"

settings = Settings()