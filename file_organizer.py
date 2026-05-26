import os
import shutil
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

CATEGORIES = {
    "Images":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                    ".webp", ".ico", ".tiff", ".heic"],
    "Documents":   [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt",
                    ".pptx", ".txt", ".rtf", ".csv", ".md", ".odt"],
    "Videos":      [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
                    ".webm", ".m4v", ".mpg", ".mpeg"],
    "Audio":       [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma",
                    ".m4a", ".aiff"],
    "Archives":    [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2",
                    ".xz", ".tgz"],
    "Code":        [".py", ".js", ".ts", ".html", ".css", ".java",
                    ".cpp", ".c", ".sh", ".json", ".xml", ".yaml",
                    ".yml", ".go", ".rs", ".rb", ".php"],
    "Executables": [".exe", ".msi", ".dmg", ".apk", ".deb", ".rpm", ".app"],
    "Fonts":       [".ttf", ".otf", ".woff", ".woff2", ".eot"],
}


def get_category(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"


def file_hash(file_path: Path) -> str:
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_conflict(dest: Path, auto_rename: bool) -> Path | None:
    if not dest.exists():
        return dest
    if auto_rename:
        stem, suffix = dest.stem, dest.suffix
        counter = 1
        while dest.exists():
            dest = dest.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        return dest
    return None


def scan_directory(directory: Path, recurse: bool) -> list[Path]:
    if recurse:
        return [p for p in directory.rglob("*") if p.is_file()]
    return [p for p in directory.iterdir() if p.is_file()]


def organize(
    directory: str,
    preview: bool = False,
    skip_duplicates: bool = True,
    auto_rename: bool = False,
    recurse: bool = False,
    categories: list[str] | None = None,
) -> dict:
    base = Path(directory).resolve()
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Directory not found: {base}")

    enabled = set(categories) if categories else set(CATEGORIES.keys()) | {"Others"}
    files = scan_directory(base, recurse)

    stats = defaultdict(int)
    seen_hashes: set[str] = set()
    log: list[str] = []

    print(f"\n{'[PREVIEW] ' if preview else ''}Organizing: {base}")
    print(f"Files found: {len(files)}\n")

    for file in files:
        category = get_category(file)

        if category not in enabled:
            stats["skipped"] += 1
            log.append(f"  SKIP  (disabled category) {file.name}")
            continue

        if skip_duplicates:
            h = file_hash(file)
            if h in seen_hashes:
                stats["duplicates"] += 1
                log.append(f"  SKIP  (duplicate) {file.name}")
                continue
            seen_hashes.add(h)

        dest_dir = base / category
        dest = dest_dir / file.name
        dest = resolve_conflict(dest, auto_rename)

        if dest is None:
            stats["skipped"] += 1
            log.append(f"  SKIP  (conflict) {file.name}")
            continue

        action = "PREVIEW" if preview else "MOVE"
        log.append(f"  {action}  {file.name}  →  {category}/")
        stats["moved"] += 1

        if not preview:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(dest))

    for line in log:
        print(line)

    print(f"\n{'Preview: ' if preview else ''}Done.")
    print(f"  Moved:      {stats['moved']}")
    print(f"  Skipped:    {stats['skipped']}")
    print(f"  Duplicates: {stats['duplicates']}")
    return dict(stats)


def main():
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by type."
    )
    parser.add_argument("directory", help="Path to the directory to organize")
    parser.add_argument(
        "--preview", action="store_true",
        help="Show what would happen without moving files"
    )
    parser.add_argument(
        "--no-skip-duplicates", dest="skip_duplicates",
        action="store_false", help="Allow duplicate files to be moved"
    )
    parser.add_argument(
        "--auto-rename", action="store_true",
        help="Automatically rename files if a conflict exists"
    )
    parser.add_argument(
        "--recurse", action="store_true",
        help="Recursively scan subfolders"
    )
    parser.add_argument(
        "--categories", nargs="+",
        help="Only organize specific categories (e.g. Images Videos Documents)"
    )

    args = parser.parse_args()
    organize(
        directory=args.directory,
        preview=args.preview,
        skip_duplicates=args.skip_duplicates,
        auto_rename=args.auto_rename,
        recurse=args.recurse,
        categories=args.categories,
    )


if __name__ == "__main__":
    main()
