import pandas as pd
import re
from datetime import datetime
from core.logger import get_logger
from core.config import settings
from infrastructure.minio_repo import MinioRepository
from infrastructure.database_repo import DatabaseRepository

logger = get_logger(__name__)

class CleanerService:
    def __init__(self):
        self.minio_repo = MinioRepository()
        self.db_repo = DatabaseRepository()

    def process_data(self):
        logger.info("Starting transformation process...")
        
        # 1. KÉO DỮ LIỆU THÔ TỪ MINIO
        raw_file_name = f"raw_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        df = self.minio_repo.download_dataframe(settings.RAW_BUCKET, raw_file_name)

        if df.empty:
            logger.warning("No raw data found in Data Lake to process.")
            return

        # 2. CLEANING LOGIC
        df.drop_duplicates(subset=["job_link"], inplace=True)
        
        before_drop = len(df)
        exclude_cols = ["salary", "experience", "job_requirements"]
        cols_to_check = [col for col in df.columns if col not in exclude_cols]

        for col in cols_to_check:
            df = df[df[col].notna()]
            df = df[~df[col].astype(str).str.strip().str.lower().isin(["n/a", "nan", "", "none"])]

        if before_drop - len(df) > 0:
            logger.info(f"Dropped {before_drop - len(df)} incomplete rows.")

        df.fillna("N/A", inplace=True)

        df["salary"] = (
            df["salary"].astype(str).str.replace("Xem nhanh", "", regex=False)
            .str.replace("\n", " ").str.replace(r"\s+", " ", regex=True).str.strip()
        )
        df.loc[df["salary"].str.lower() == "đang cập nhật", "salary"] = "Negotiable"

        def format_experience(exp):
            exp = str(exp).strip()
            match = re.search(r"OccupationalExperienceRequirements,\s*(\d+)", exp)
            if match:
                months = int(match.group(1))
                if months >= 12: return f"{months // 12} years"
                elif months > 0: return f"{months} months"
            targets = ["không yêu cầu", "nan", "n/a", "", "cập nhật", "đang cập nhật", "no requirements"]
            if exp.lower() in targets: return "Requirements applied"
            return exp

        df["experience"] = df["experience"].apply(format_experience)

        def smart_format(text):
            if str(text) == "N/A": return text
            lines = str(text).split('\n')
            fmt = []
            keys = ["mô tả", "yêu cầu", "quyền lợi", "phúc lợi", "description", "requirements", "benefits", "who we are", "about", "responsibilities"]
            for l in lines:
                l = l.strip()
                if not l: continue
                if len(l) < 55 and (l.isupper() or any(l.lower().startswith(k) for k in keys) or l.endswith(":")):
                    fmt.append(f"\n#### {l.upper()}")
                else:
                    if not l.startswith(("-", "*", "•", "+")): fmt.append(f"- {l}")
                    else: fmt.append(l)
            return "  \n".join(fmt)

        if "job_description" in df.columns:
            df["job_description"] = df["job_description"].apply(smart_format)
        if "job_requirements" in df.columns:
            df.drop(columns=["job_requirements"], inplace=True)

        logger.info(f"Transformation complete. Valid rows: {len(df)}")

        # 3. LOAD: LƯU BẢN SẠCH LÊN MINIO & ĐẨY VÀO DATABASE
        clean_file_name = f"cleaned_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        self.minio_repo.upload_dataframe(df, settings.CLEAN_BUCKET, clean_file_name)
        self.db_repo.save_dataframe(df, "it_jobs")