from sqlalchemy import create_engine
from core.config import settings
from core.logger import get_logger
import pandas as pd

logger = get_logger(__name__)

class DatabaseRepository:
    def __init__(self):
        self.engine = create_engine(
            f'postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
        )
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str):
        try:
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            logger.info(f"Successfully loaded data into PostgreSQL table: {table_name}")
        except Exception as e:
            logger.error(f"PostgreSQL connection/upload error: {e}")