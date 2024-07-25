import os
import shutil
import sys
from pathlib import Path
from threading import Thread
from queue import Queue

def copy_file_to_dest(file_path, dest_dir):
    ext = file_path.suffix[1:]  # Get the extension without the dot
    if not ext:
        return
    dest_path = dest_dir / ext
    dest_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(file_path, dest_path / file_path.name)

def worker(queue, dest_dir):
    while True:
        file_path = queue.get()
        if file_path is None:
            break
        try:
            copy_file_to_dest(file_path, dest_dir)
        finally:
            queue.task_done()

def process_directory(src_dir, dest_dir, num_threads=4):
    queue = Queue()
    threads = []
    for _ in range(num_threads):
        thread = Thread(target=worker, args=(queue, dest_dir))
        thread.start()
        threads.append(thread)

    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = Path(root) / file
            queue.put(file_path)
    
    queue.join()

    for _ in range(num_threads):
        queue.put(None)
    for thread in threads:
        thread.join()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_directory> [<destination_directory>]")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    dest_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('dist')

    if not src_dir.is_dir():
        print(f"Source directory {src_dir} does not exist.")
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)

    process_directory(src_dir, dest_dir)

if __name__ == "__main__":
    main()