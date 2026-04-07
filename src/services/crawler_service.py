import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from core.logger import get_logger
from core.config import settings
from infrastructure.minio_repo import MinioRepository

logger = get_logger(__name__)

JOB_POSITIONS = [
    "Backend Developer",
    "Frontend Developer",
    "Fullstack Developer",
    "Mobile Developer",
    "Game Developer",
    
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "AI Engineer",
    "Machine Learning Engineer",
    
    "Tester",
    "QA Engineer",
    "QC Engineer",
    "Automation Test",
    
    "DevOps Engineer",
    "Cloud Engineer",
    "System Administrator",
    "Network Engineer",
    "Security Engineer",
    "Embedded Engineer",
    
    "Business Analyst", 
    "Product Manager",
    "Project Manager",
    "Scrum Master",
    "UI/UX Designer"
]
BASE_URL = "https://123job.vn"
HEADERS = {"User-Agent": "Mozilla/5.0"}

class CrawlerService:
    def __init__(self):
        self.minio_repo = MinioRepository()

    def build_search_url(self, job_name: str, page: int) -> str:
        return f"{BASE_URL}/tuyen-dung?q={job_name.replace(' ', '+')}&page={page}"

    def extract_jobs(self):
        logger.info("Starting extraction process...")
        all_jobs = []

        for position in JOB_POSITIONS:
            logger.info(f"Crawling position: {position}")
            page = 1
            
            while True:
                url = self.build_search_url(position, page)
                try:
                    response = requests.get(url, headers=HEADERS, timeout=15)
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_items = soup.find_all("div", class_="job__list-item")
                    
                    if not job_items:
                        logger.info(f"Completed scanning for '{position}'.")
                        break 

                    for item in job_items: 
                        try:
                            title_tag = item.find("h2", class_="job__list-item-title")
                            if not title_tag: continue
                            a_tag = title_tag.find("a")
                            job_name = a_tag.get_text(strip=True)
                            job_link = a_tag["href"]
                            if not job_link.startswith("http"):
                                job_link = BASE_URL + job_link

                            company_tag = item.find("div", class_="job__list-item-company")
                            company = company_tag.find("span").get_text(strip=True) if company_tag else "N/A"

                            experience, salary, location, full_description = "N/A", "N/A", "N/A", "N/A"
                            time.sleep(random.uniform(1.5, 3.0))
                            
                            res_detail = requests.get(job_link, headers=HEADERS, timeout=10)
                            soup_detail = BeautifulSoup(res_detail.text, "html.parser")

                            attr_items = soup_detail.find_all("div", class_="attr-item")
                            for attr in attr_items:
                                full_text = attr.get_text(strip=True).lower()
                                value_div = attr.find("div", class_="value")
                                
                                if value_div:
                                    value_text = value_div.get_text(strip=True)
                                    if "kinh nghiệm" in full_text: experience = value_text
                                    elif "lương" in full_text: salary = value_text
                                    elif "địa điểm" in full_text: location = value_text

                            if location == "N/A":
                                address_div = soup_detail.find("div", class_="job-detail__info-address")
                                if address_div: location = address_div.get_text(strip=True).replace("Địa điểm làm việc:", "").strip()

                            content_div = soup_detail.find("div", class_="content-collapse")
                            if content_div: full_description = content_div.get_text(separator="\n").strip()

                            all_jobs.append({
                                "position_search": position, "job_name": job_name,
                                "job_link": job_link, "company": company,
                                "location": location, "salary": salary,
                                "experience": experience, "job_description": full_description,
                                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                        except Exception as e:
                            logger.warning(f"Error processing item: {e}")
                            continue
                    page += 1
                except Exception as e:
                    logger.error(f"Network error on page {page}: {url} - {e}")
                    break

        df = pd.DataFrame(all_jobs)
        logger.info(f"Extraction complete. Total records: {len(df)}")
        
        file_name = f"raw_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
        self.minio_repo.upload_dataframe(df, settings.RAW_BUCKET, file_name)