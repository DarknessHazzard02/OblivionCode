"""
File Organizer v2 - sorts files into Category/Subcategory folders by extension.
Main route: your Documents folder (detected automatically, OneDrive-aware).
Made by: Hazzard
"""

import csv
import os
import shutil
import sys
from datetime import datetime

# =====================================================================
# CONFIGURATION
# =====================================================================
CATEGORIES = {
    "Documents": {
        "Excel": [".csv", ".xls", ".xlsx", ".xlsm", ".xlsb", ".xltx", ".xltm", ".ods"],
        "Word": [".doc", ".docx", ".docm", ".dotx", ".dotm", ".rtf", ".odt"],
        "PDF": [".pdf"],
        "PowerPoint": [
            ".ppt",
            ".pptx",
            ".pptm",
            ".potx",
            ".potm",
            ".ppsx",
            ".pps",
            ".odp",
        ],
        "PowerBI": [".pbix", ".pbit", ".pbids", ".pbip"],
        "Access": [".accdb", ".mdb"],
        "Visio": [".vsd", ".vsdx", ".vsdm"],
        "OneNote": [".one"],
        "Text": [".txt", ".md", ".log"],
    },
    "Pictures": {
        "JPEG": [".jpg", ".jpeg", ".jfif"],
        "PNG": [".png"],
        "GIF": [".gif"],
        "Vector": [".svg", ".ai", ".eps"],
        "Photoshop": [".psd"],
        "RAW": [".raw", ".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf"],
        "Icons": [".ico"],
        "Other Images": [".bmp", ".tif", ".tiff", ".webp", ".heic", ".heif"],
    },
    "Videos": {
        "MP4": [".mp4", ".m4v"],
        "MOV": [".mov"],
        "AVI": [".avi"],
        "MKV": [".mkv"],
        "WMV": [".wmv"],
        "WebM": [".webm"],
        "Other Videos": [".flv", ".mpeg", ".mpg", ".3gp"],
    },
    "Audio": {
        "MP3": [".mp3"],
        "WAV": [".wav"],
        "FLAC": [".flac"],
        "AAC-M4A": [".aac", ".m4a"],
        "OGG": [".ogg", ".opus"],
        "WMA": [".wma"],
        "MIDI": [".mid", ".midi"],
        "AIFF": [".aif", ".aiff"],
    },
    "Code": {
        "Python": [".py", ".ipynb", ".pyw"],
        "SQL": [".sql"],
        "PowerQuery": [".pq", ".m"],
        "VBA": [".bas", ".cls", ".frm", ".vba"],
        "Scripts": [".ps1", ".bat", ".cmd", ".sh"],
        "Web": [".html", ".htm", ".css", ".js", ".ts"],
        "Data": [".json", ".xml", ".yaml", ".yml", ".parquet"],
    },
    "Installers": {
        "EXE": [".exe"],
        "MSI": [".msi"],
    },
}
# Compressed files (.zip, .rar, .7z, ...) and any unknown extension go to Others/<EXT>
OTHERS_FOLDER = "Others"
OLDER_VERSIONS_FOLDER = (
    "_Older Versions"  # Duplicates that lose (older modified date) go here
)
LOGS_FOLDER = "_Organizer Logs"
PROTECT_GIT_REPOS = (
    True  # Never touch folders that contain a .git folder (e.g. Documents\Github repos)
)
SKIP_FILES = {"desktop.ini", "thumbs.db", ".ds_store"}
SKIP_PREFIXES = ("~$", ".~lock")
SKIP_EXTENSIONS = {".tmp", ".crdownload", ".part", ".lnk", ".url"}
DEFAULT_IGNORED = [
    # r"C:\Users\pabloa02\OneDrive - Nidec (1)\Desktop",
    # r"C:\Users\pabloa02\OneDrive - Nidec (1)\Documents\Github",
]
PREVIEW_ROWS_ON_SCREEN = 25


# =====================================================================
# PATH HELPERS
# =====================================================================
def clean_path(raw):
    return os.path.normcase(
        os.path.abspath(
            os.path.expandvars(os.path.expanduser(raw.strip().strip('"').strip("'")))
        )
    )


def is_inside(path, parent):
    try:
        return os.path.commonpath([path, parent]) == parent
    except ValueError:
        return False


def detect_documents():
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            )
            value, _ = winreg.QueryValueEx(key, "Personal")
            path = os.path.expandvars(value)
            if os.path.isdir(path):
                return path
        except OSError:
            pass
    for env in ("OneDriveCommercial", "OneDrive"):
        base = os.environ.get(env)
        if base and os.path.isdir(os.path.join(base, "Documents")):
            return os.path.join(base, "Documents")
    return os.path.join(os.path.expanduser("~"), "Documents")


def unique_target(target):
    if not os.path.exists(target):
        return target
    base, ext = os.path.splitext(target)
    i = 1
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"


def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


# =====================================================================
# PROMPTS
# =====================================================================
def ask_path(prompt, default, must_exist=True):
    while True:
        raw = input(f"{prompt}\n  [Enter = {default}]: ").strip()
        path = clean_path(raw) if raw else clean_path(default)
        if must_exist and not os.path.isdir(path):
            print(f"  Folder not found: {path}")
            continue
        return path


def ask_yes_no(prompt, default=True):
    raw = input(prompt + (" [Y/n]: " if default else " [y/N]: ")).strip().lower()
    return default if not raw else raw in ("y", "yes", "s", "si", "sí")


def ask_ignored_paths():
    ignored = [clean_path(p) for p in DEFAULT_IGNORED]
    print("\nFolders to IGNORE/LOCK (one per line, empty line to finish):")
    while True:
        raw = input("  Ignore path: ").strip()
        if not raw:
            break
        path = clean_path(raw)
        if not os.path.isdir(path):
            print(f"  Warning: folder not found, it will still be ignored: {path}")
        ignored.append(path)
    return ignored


# =====================================================================
# CORE
# =====================================================================
def build_lookup():
    lookup = {}
    for category, subs in CATEGORIES.items():
        for sub, exts in subs.items():
            for ext in exts:
                lookup[ext.lower()] = (category, sub)
    return lookup


def managed_folders(destination):
    names = list(CATEGORIES.keys()) + [
        OTHERS_FOLDER,
        OLDER_VERSIONS_FOLDER,
        LOGS_FOLDER,
    ]
    return [os.path.normcase(os.path.join(destination, n)) for n in names]


def should_skip_file(name):
    low = name.lower()
    return (
        low in SKIP_FILES
        or low.startswith(SKIP_PREFIXES)
        or os.path.splitext(low)[1] in SKIP_EXTENSIONS
    )


def collect_files(source, blocked):
    files, protected = [], []
    for root, dirs, names in os.walk(source):
        if PROTECT_GIT_REPOS and ".git" in dirs:
            protected.append(root)
            dirs[:] = []
            continue
        dirs[:] = [
            d
            for d in dirs
            if not any(
                is_inside(os.path.normcase(os.path.join(root, d)), b) for b in blocked
            )
        ]
        for name in names:
            if not should_skip_file(name):
                files.append(os.path.join(root, name))
    return files, protected


def target_folder(path, destination, lookup):
    ext = os.path.splitext(path)[1].lower()
    if ext in lookup:
        category, sub = lookup[ext]
    else:
        category, sub = OTHERS_FOLDER, (ext[1:].upper() if ext else "No Extension")
    return os.path.join(destination, category, sub)


def archive_path(path, folder, destination):
    rel = os.path.relpath(folder, destination)
    stem, ext = os.path.splitext(os.path.basename(path))
    stamp = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H%M%S")
    return os.path.join(
        destination, OLDER_VERSIONS_FOLDER, rel, f"{stem} (modified {stamp}){ext}"
    )


def plan_actions(files, destination, lookup, mode):
    groups = {}
    for path in files:
        folder = target_folder(path, destination, lookup)
        target = os.path.join(folder, os.path.basename(path))
        groups.setdefault(os.path.normcase(target), (target, folder, []))[2].append(
            path
        )
    actions = []  # (action, source, target, modified, note)
    for target, folder, sources in groups.values():
        sources = [
            s for s in sources if os.path.normcase(s) != os.path.normcase(target)
        ]
        if not sources:
            continue
        existing = target if os.path.exists(target) else None
        candidates = [(s, os.path.getmtime(s), False) for s in sources]
        if existing:
            candidates.append((existing, os.path.getmtime(existing), True))
        candidates.sort(key=lambda c: c[1], reverse=True)
        winner, others = candidates[0], candidates[1:]
        dup_note = (
            f"Duplicate name: {len(candidates)} versions, newest kept" if others else ""
        )
        for path, mtime, is_existing in others:
            if is_existing:
                actions.append(
                    (
                        "ARCHIVE OLDER",
                        path,
                        archive_path(path, folder, destination),
                        mtime,
                        "Existing file in destination is older",
                    )
                )
            elif mode == "move":
                actions.append(
                    (
                        "ARCHIVE OLDER",
                        path,
                        archive_path(path, folder, destination),
                        mtime,
                        "Older version",
                    )
                )
            else:
                actions.append(
                    ("SKIP OLDER", path, "", mtime, "Older version, not copied")
                )
        if not winner[2]:
            actions.append((mode.upper(), winner[0], target, winner[1], dup_note))
    return actions


def run_action(action, src, dst):
    if action in ("SKIP OLDER",):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if action == "COPY":
        shutil.copy2(src, dst)
    else:
        shutil.move(src, dst)


def remove_empty_folders(source, blocked):
    removed = 0
    for root, dirs, files in os.walk(source, topdown=False):
        root_n = os.path.normcase(root)
        if root_n == source or any(is_inside(root_n, b) for b in blocked):
            continue
        try:
            leftovers = [f for f in os.listdir(root) if f.lower() != "desktop.ini"]
            if not leftovers:
                for f in os.listdir(root):
                    os.remove(os.path.join(root, f))
                os.rmdir(root)
                removed += 1
        except OSError:
            pass
    return removed


def write_log(rows, destination, dry_run):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(destination, LOGS_FOLDER)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{'PREVIEW' if dry_run else 'RUN'}_{stamp}.csv")
    with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Action", "Status", "Source", "Target", "Last Modified", "Note", "Error"]
        )
        writer.writerows(rows)
    return log_path


# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 64)
    print(" FILE ORGANIZER v2  |  Made by: Hazzard")
    print("=" * 64)
    documents = detect_documents()
    source = ask_path("\nSource folder (bulk files):", documents)
    destination = ask_path("Destination folder (main route):", source, must_exist=False)
    ignored = ask_ignored_paths()
    if any(is_inside(source, i) for i in ignored) or any(
        is_inside(destination, i) for i in ignored
    ):
        print("\nSource or destination is inside an ignored path. Nothing to do.")
        return
    mode = (
        "copy"
        if input("\nMove or Copy files? [M/c]: ").strip().lower().startswith("c")
        else "move"
    )
    dry_run = ask_yes_no("Preview only (dry run, no files touched)?", default=True)
    blocked = ignored + managed_folders(destination)
    if not is_inside(destination, source):
        blocked.append(destination)
    files, protected = collect_files(source, blocked)
    actions = plan_actions(files, destination, build_lookup(), mode)
    if not actions:
        print("\nNothing to organize. Everything is already in place.")
        return
    summary = {}
    for action, src, dst, _, _ in actions:
        key = (
            action
            if action != mode.upper()
            else os.path.relpath(os.path.dirname(dst), destination)
        )
        summary[key] = summary.get(key, 0) + 1
    print("\n" + "-" * 64)
    print(f" Source        : {source}")
    print(f" Destination   : {destination}")
    print(f" Ignored       : {len(ignored)} path(s)")
    for i in ignored:
        print(f"   - {i}")
    print(f" Git repos protected: {len(protected)}")
    for p in protected:
        print(f"   - {p}")
    print(f" Files to process  : {len(actions)}")
    print(
        f" Mode              : {mode.upper()}{'  (PREVIEW / DRY RUN)' if dry_run else ''}"
    )
    print("-" * 64)
    print("\nPLAN BY FOLDER")
    for folder, n in sorted(summary.items()):
        print(f"  {folder:<40} {n:>6}")
    if dry_run:
        print(f"\nFIRST {min(PREVIEW_ROWS_ON_SCREEN, len(actions))} ACTIONS")
        for action, src, dst, mtime, note in actions[:PREVIEW_ROWS_ON_SCREEN]:
            print(f"  [{action}] {os.path.relpath(src, source)}")
            print(
                f"      -> {os.path.relpath(dst, destination) if dst else '(not copied)'}  | modified {fmt_time(mtime)} {('| ' + note) if note else ''}"
            )
        rows = [[a, "PREVIEW", s, d, fmt_time(m), n, ""] for a, s, d, m, n in actions]
        print(f"\nFull preview saved to: {write_log(rows, destination, True)}")
        print(
            "Nothing was moved. Run again and answer 'n' to the preview question to apply."
        )
        return
    if not ask_yes_no(f"\nProceed with {len(actions)} action(s)?", default=False):
        print("Cancelled. No files were touched.")
        return
    rows, ok, errors = [], 0, 0
    for action, src, dst, mtime, note in actions:
        try:
            if dst and action != "SKIP OLDER":
                dst = unique_target(dst) if action == "ARCHIVE OLDER" else dst
            run_action(action, src, dst)
            rows.append([action, "OK", src, dst, fmt_time(mtime), note, ""])
            ok += 1
        except Exception as e:
            rows.append([action, "ERROR", src, dst, fmt_time(mtime), note, str(e)])
            errors += 1
    removed = remove_empty_folders(source, blocked) if mode == "move" else 0
    print(f"\n  OK: {ok}   ERRORS: {errors}   Empty folders removed: {removed}")
    print(f"  Log saved to: {write_log(rows, destination, False)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    input("\nPress Enter to exit...")
# Made by: Hazzard
