from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('smart_scrapy',
          default_args=default_args,
          description='Run Scrapy Spider with BashOperator',
          schedule_interval=timedelta(days=1))

run_spider_task = BashOperator(
    task_id='run_scrapy',
    bash_command='cd /root/whiskyscraper && scrapy crawl whisky -o output.json',
    dag=dag)
