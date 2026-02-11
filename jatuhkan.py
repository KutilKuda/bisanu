import os
import requests
from urllib.parse import urljoin

# URL file GitHub (format raw GitHub URL)
file_urls = [
    "https://raw.githubusercontent.com/KutilKuda/bisanu/main/wallp.jpg",
    "https://github.com/KutilKuda/bisanu/raw/refs/heads/main/icon.svg",
    "https://github.com/KutilKuda/bisanu/raw/refs/heads/main/bisanu.py"
]

# Nama file lokal
local_filenames = ["wallp.jpg", "icon.svg", "bisanu.py"]

def download_files():
    for url, filename in zip(file_urls, local_filenames):
        try:
            print(f"Downloading {filename}...")
            
            # Download file
            response = requests.get(url)
            response.raise_for_status()  # Cek jika ada error
            
            # Simpan file
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ {filename} downloaded successfully!")
            
            # Jika file Python, berikan permission execute
            if filename.endswith('.py'):
                os.chmod(filename, 0o755)
                print(f"✓ {filename} set as executable")
                
        except Exception as e:
            print(f"✗ Error downloading {filename}: {e}")

def run_python_script():
    """Jalankan file Python yang sudah didownload"""
    python_file = "bisanu.py"
    if os.path.exists(python_file):
        print(f"\nRunning {python_file}...")
        os.system(f"python3 {python_file}")
    else:
        print(f"File {python_file} not found!")

if __name__ == "__main__":
    # Download semua file
    download_files()
    
    # Jalankan file Python (opsional)
    run_python_script()