import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.crawler_service import CrawlerService

if __name__ == "__main__":
    crawler = CrawlerService()
    crawler.extract_jobs()