from minio import Minio
from core.config import settings
from core.logger import get_logger
from io import BytesIO
import pandas as pd

logger = get_logger(__name__)

class MinioRepository:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
    
    def create_bucket_if_not_exists(self, bucket_name: str):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"Error checking/creating bucket {bucket_name}: {e}")
            
    def upload_dataframe(self, df: pd.DataFrame, bucket_name: str, object_name: str):
        self.create_bucket_if_not_exists(bucket_name)
        try:
            csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
            csv_buffer = BytesIO(csv_bytes)
            self.client.put_object(
                bucket_name,
                object_name,
                data=csv_buffer,
                length=len(csv_bytes),
                content_type='application/csv'
            )
            logger.info(f"Successfully uploaded {object_name} to {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to upload {object_name}: {e}")

    def download_dataframe(self, bucket_name: str, object_name: str) -> pd.DataFrame:
        try:
            response = self.client.get_object(bucket_name, object_name)
            df = pd.read_csv(BytesIO(response.read()), encoding='utf-8-sig')
            response.close()
            response.release_conn()
            logger.info(f"Successfully downloaded {object_name} from {bucket_name}")
            return df
        except Exception as e:
            logger.error(f"Failed to download {object_name}: {e}")
            return pd.DataFrame()