from pathlib import Path
import shutil

DOWNLOADS = Path(r"C:\Users\student\Downloads")
#정리할 폴더


EXT_MAP = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip"},
}

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def unique_target(target: Path) -> Path:
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def classify_and_move():
    if not DOWNLOADS.exists() or not DOWNLOADS.is_dir():
        print(f"Downloads 폴더가 없습니다: {DOWNLOADS}")
        return

    # 미리 폴더 생성
    dest_dirs = {name: DOWNLOADS / name for name in EXT_MAP.keys()}
    for d in dest_dirs.values():
        ensure_dir(d)

    moved = 0
    for p in DOWNLOADS.iterdir():
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        moved_to = None
        for name, exts in EXT_MAP.items():
            if ext in exts:
                dest = dest_dirs[name] / p.name
                dest = unique_target(dest)
                shutil.move(str(p), str(dest))
                moved += 1
                moved_to = dest
                break
        if moved_to:
            print(f"이동: {p.name} -> {moved_to}")
    print(f"완료: {moved}개 파일 이동됨.")

if __name__ == "__main__":
    classify_and_move()