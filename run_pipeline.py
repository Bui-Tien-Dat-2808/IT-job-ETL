import subprocess
import time
import os

def run_script(script_name, working_dir):    
    start_time = time.time()

    try:
        # Use subprocess to run the python script
        process = subprocess.run(
            ["python", script_name],
            cwd=working_dir,
            check=True # Raise an error immediately if the script fails
        )

        end_time = time.time()
        return True

    except subprocess.CalledProcessError as e:
        print(f"\nCritical error in: {script_name}")
        print(f"Error code details: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n'python' command not found. Please check your environment variables.")
        return False

def main():
    total_start_time = time.time()

    # Get the absolute path of the root directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Crawl Data (Extract)
    crawl_dir = os.path.join(base_dir, "crawl")
    if not run_script("crawl_data.py", crawl_dir):
        print("\nFailure in crawling.")
        return

    # Clean & Load Data (Transform & Load)
    clean_dir = os.path.join(base_dir, "clean")
    if not run_script("clean_data.py", clean_dir):
        print("\nFailure in cleaning.")
        return

    total_end_time = time.time()

if __name__ == "__main__":
    main()