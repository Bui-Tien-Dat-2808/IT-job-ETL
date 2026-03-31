import pandas as pd
import re
import os
from sqlalchemy import create_engine

def load_to_postgres(df):
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres' 
    DB_HOST = 'postgres'
    DB_PORT = '5432'
    DB_NAME = 'IT_job_data'
    
    try:
        # Create database connection
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

        # Push DataFrame to database
        df.to_sql('it_jobs', engine, if_exists='replace', index=False)

        print("Data successfully loaded into DB.")
    except Exception as e:
        print(f"Error pushing data to Database: {e}")

def clean_jobs():
    print("Starting data cleaning process...")

    # Path configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "..", "crawl", "data", "raw_jobs.csv")
    output_dir = os.path.join(current_dir, "data")
    output_file = os.path.join(output_dir, "cleaned_jobs.csv")

    if not os.path.exists(input_file):
        print(f"ERROR: File '{input_file}' not found!")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory for cleaned data at: {output_dir}")

    try:
        df = pd.read_csv(input_file, encoding="utf-8-sig")
        print(f"📂 Đã đọc file raw. Số lượng ban đầu: {len(df)} dòng.")

        if df.empty:
            print("⚠️ Cảnh báo: File dữ liệu rỗng.")
            return
        
        # Handle duplicatas
        df.drop_duplicates(subset=["job_link"], inplace=True)
        
        # Check and remove rows with insufficient valid data
        before_drop = len(df)

        # Get list of columns to check
        exclude_cols = ["salary", "experience", "job_requirements"]
        cols_to_check = [col for col in df.columns if col not in exclude_cols]

        for col in cols_to_check:
            # Filter out rows with actual null values (NaN)
            df = df[df[col].notna()]
            # Filter out rows containing "N/A", "nan", or empty strings
            df = df[~df[col].astype(str).str.strip().str.lower().isin(["n/a", "nan", "", "none"])]

        after_drop = len(df)
        if before_drop - after_drop > 0:
            print(f"    -> Removed {before_drop - after_drop} rows with insufficient valid data.")
        # Fill remaining empty values with N/A
        df.fillna("N/A", inplace=True)

        # Salary standardization
        df["salary"] = (
            df["salary"]
            .astype(str)
            .str.replace("Xem nhanh", "", regex=False)
            .str.replace("\n", " ")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
        df.loc[df["salary"].str.lower() == "đang cập nhật", "salary"] = "Thoả thuận"
        
        # Experience standardization
        def format_experience(exp):
            exp = str(exp).strip()
            
            match = re.search(r"OccupationalExperienceRequirements,\s*(\d+)", exp)
            if match:
                months = int(match.group(1))
                if months >= 12:
                    return f"{months // 12} năm"
                elif months > 0:
                    return f"{months} tháng"
            
            targets = ["không yêu cầu", "nan", "n/a", "", "cập nhật", "đang cập nhật", "no requirements"]
            if exp.lower() in targets:
                return "Có yêu cầu"
            
            return exp
        
        df["experience"] = df["experience"].apply(format_experience)

        # Heading and formatting for job descriptions
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
                    if not l.startswith(("-", "*", "•", "+")):
                        fmt.append(f"- {l}")
                    else:
                        fmt.append(l)
            return "  \n".join(fmt)

        if "job_description" in df.columns:
            df["job_description"] = df["job_description"].apply(smart_format)

        if "job_requirements" in df.columns:
            df.drop(columns=["job_requirements"], inplace=True)

        # Save file and push to DB
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"SUCCESS! Saved {len(df)} cleaned data rows.")
        load_to_postgres(df)

    except PermissionError:
        print(f"ERROR: Cannot write file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clean_jobs()