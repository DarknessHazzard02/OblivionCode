from pathlib import Path

folder = Path(
    input("Enter folder path: ").strip()
)
prefix = input("Enter new prefix: ").strip()

if not folder.is_dir():
    print("Folder not found!")
    exit()

files = [
    f for f in folder.iterdir()
    if f.is_file()
]

if not files:
    print("No files found!")
    exit()


print("\n" + "=" * 55)
print("             SMART FILE RENAMER")
print("=" * 55)

for index, file in enumerate(files, 1):
    new_name = f"{prefix}_{index}{file.suffix}"
    new_path = file.parent / new_name

    if new_path.exists():
        print(f"Skipped: {file.name}")
        continue

    file.rename(new_path)
    print(f"{file.name} -> {new_name}")

print("=" * 55)
print(f"✔ {len(files)} files processed.")