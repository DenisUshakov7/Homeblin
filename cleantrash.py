#!/usr/bin/env python3
import os
import time
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Smart Trash Cleaner: автоматическая очистка корзины"
    )
    parser.add_argument(
        "--trash_folder_path",
        required=True,
        help="Путь до папки-корзины"
    )
    parser.add_argument(
        "--age_thr",
        required=True,
        type=int,
        help="Порог возраста файлов в секундах"
    )
    return parser.parse_args()

def log_removal(path, log_file):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - Removed: {path}\n")

def clean_trash(folder, age_thr, log_file):
    now = time.time()
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            try:
                age = now - os.path.getmtime(path)
                if age > age_thr:
                    os.remove(path)
                    log_removal(path, log_file)
            except Exception as e:
                print(f"Error removing file {path}: {e}", file=sys.stderr)
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    log_removal(dir_path, log_file)
            except Exception as e:
                print(f"Error removing dir {dir_path}: {e}", file=sys.stderr)

def main():
    args = parse_args()
    trash_folder = os.path.normpath(args.trash_folder_path)
    age_thr = args.age_thr
    log_file = os.path.join(trash_folder, "clean_trash.log")
    while True:
        clean_trash(trash_folder, age_thr, log_file)
        time.sleep(1)

main()
