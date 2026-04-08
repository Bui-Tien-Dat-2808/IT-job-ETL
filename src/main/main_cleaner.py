import sys
import os

src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if src_dir not in sys.path:
    sys.path.append(src_dir)

from services.cleaner_service import CleanerService

if __name__ == "__main__":
    cleaner = CleanerService()
    cleaner.process_data()