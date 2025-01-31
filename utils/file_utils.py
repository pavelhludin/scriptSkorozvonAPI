# utils/file_utils.py

import json
import os

def save_to_json(data, filename):
    """Сохраняет данные в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в файл {filename}")

def create_directory(directory):
    """Создает директорию, если она не существует."""
    os.makedirs(directory, exist_ok=True)