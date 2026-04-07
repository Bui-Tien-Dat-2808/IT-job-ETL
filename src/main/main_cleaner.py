import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cleaner_service import CleanerService

if __name__ == "__main__":
    cleaner = CleanerService()
    cleaner.process_data()