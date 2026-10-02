import os
import shutil
from pathlib import Path

folder = Path(input("Enter folder path: ").strip())

file_types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".java"]
}

def get_category(extension):
    extension = extension.lower()

    for category, extensions in file_types.items():
        if extension in extensions:
            return category

    return "Others"

if not folder.is_dir():
    print("Folder not found!")
    exit()

moved = 0

for file in folder.iterdir():
    if not file.is_file():
        continue

    category = get_category(file.suffix)
    target_folder = folder / category

    target_folder.mkdir(exist_ok=True)
    destination = target_folder / file.name

    if destination.exists():
        destination = (
            target_folder /
            f"{file.stem}_{moved}{file.suffix}"
        )

    shutil.move(str(file), str(destination))
    print(f"Moved: {file.name} -> {category}/")
    moved += 1

print(f"\n✔ {moved} files organized successfully.")