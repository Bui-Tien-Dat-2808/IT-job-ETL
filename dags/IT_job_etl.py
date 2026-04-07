from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default configuration for the pipeline
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5), # Retry after 5 minutes if an error occurs
}

# Initialize DAG, scheduled to run daily at 00:00
with DAG(
    'it_jobs_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline to crawl and process IT job data',
    schedule_interval='0 0 * * *', 
    catchup=False,
    tags=['it_jobs', 'etl']
) as dag:

    # Task 1: Run crawl task
    crawl_task = BashOperator(
        task_id='extract_data',
        bash_command='cd /opt/airflow/src && python main_crawler.py'
    )

    # Task 2: Run clean & load task
    clean_load_task = BashOperator(
        task_id='transform_and_load_data',
        bash_command='cd /opt/airflow/src && python main_cleaner.py'
    )

    # Set task order
    crawl_task >> clean_load_task