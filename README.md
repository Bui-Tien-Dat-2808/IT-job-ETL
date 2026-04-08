# 🚀 End-to-End IT Job Market ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue?style=for-the-badge&logo=postgresql)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-2.8.1-017CEE?style=for-the-badge&logo=Apache%20Airflow)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)

## 📌 Overview
- An automated, containerized End-to-End ETL (Extract, Transform, Load) pipeline designed to collect IT job postings, transform raw text into structured datasets, and load them into a relational database. The entire workflow is orchestrated by **Apache Airflow** and visualized through an interactive **Streamlit** dashboard.

- This project showcases a complete Data Engineering lifecycle, transitioning from raw data extraction to a production-ready, containerized analytics environment.



## 🛠️ Architecture & Workflow

1. **Extract (Crawl):** Python scripts (`requests`, `BeautifulSoup`) scrape daily job postings across 25+ IT positions (Data Engineer, Backend, Tester, AI Engineer, etc.) from recruitment platforms. The raw data is then stored in a **MinIO** data lake (`raw-zone`).
2. **Transform (Clean):** Raw data is retrieved from MinIO. `Pandas` and `Regex` are utilized to clean HTML tags, handle missing values, standardize salary and experience formats, and format job descriptions. The cleaned data is then stored back into **MinIO** (`clean-zone`).
3. **Load:** The cleaned dataset is loaded from MinIO into a **PostgreSQL** database using `SQLAlchemy`.
4. **Orchestrate:** **Apache Airflow** schedules and monitors the pipeline via a custom DAG, ensuring the jobs run sequentially (Extract -> Transform & Load) at 00:00 daily.
5. **Visualize:** A **Streamlit** web application connects to the PostgreSQL database to serve real-time job market insights and filtering capabilities.

## 📁 Project Structure

```text
├── 📁 dags
│   └── 🐍 IT_job_etl.py
├── 📁 src
│   ├── 📁 core
│   │   ├── 🐍 config.py
│   │   └── 🐍 logger.py
│   ├── 📁 infrastructure
│   │   ├── 🐍 database_repo.py
│   │   └── 🐍 minio_repo.py
│   ├── 📁 main
│   │   ├── 🐍 main_cleaner.py
│   │   └── 🐍 main_crawler.py
│   └── 📁 services
│       ├── 🐍 cleaner_service.py
│       └── 🐍 crawler_service.py
├── ⚙️ .env.example
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 app.py
├── ⚙️ docker-compose.yaml
└── 📄 requirements.txt
```

## ⚙️ How to Run Locally
### Since the entire application is containerized, you can launch the pipeline and the dashboard with a single command.

### Prerequisites
- Docker & Docker Desktop installed.

### Steps
- Start the airflow-init service for the first time. After that, you don't need to run this step:
```bash
docker-compose up airflow-init
```

- Start the services using Docker Compose:
```bash
docker-compose up -d
```

### Access the UIs
- Apache Airflow (Orchestration): Navigate to http://localhost:8080 (Default login: admin / admin). Unpause and trigger the it_jobs_etl_pipeline DAG.
    - *This DAG may take up to several hours to complete, depending on the number of professions you choose*

- MinIO (Data Lake): Navigate to http://localhost:9001 (Default login: ROOT_USER, CHANGEME123)

- Streamlit (Dashboard): Navigate to http://localhost:8501 to explore the cleaned data.

### To shut down the services
```bash
docker-compose down
```
## 📈 Future Improvements
- Implement Data Quality checks before loading into PostgreSQL.

- Migrate the database to a cloud provider (e.g., AWS RDS or Supabase).

- Expand data sources to multiple recruitment platforms.