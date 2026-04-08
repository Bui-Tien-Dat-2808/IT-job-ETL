import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "IT_job_data")
    
    _raw_minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ENDPOINT = _raw_minio_endpoint.replace("http://", "").replace("https://", "").split("/")[0]
    MINIO_ACCESS_KEY  = os.getenv("MINIO_ACCESS_KEY", "ROOT_USER")
    MINIO_SECRET_KEY  = os.getenv("MINIO_SECRET_KEY", "CHANGEME123")
    
    RAW_BUCKET = "raw-zone"
    CLEAN_BUCKET = "clean-zone"

settings = Settings()