import shutil
from pathlib import Path


def copy_dir(source: Path, dest: Path):
    """Delete contents of dest then copy everything from source."""
    # Ensure dest exists
    dest.mkdir(parents=True, exist_ok=True)

    # Remove everything inside destination
    for item in dest.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Copy everything from source to destination
    for item in source.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


# Paths
root = Path(__file__).resolve().parent.parent
source_examples = root / "tests/examples"
source_xl = root / "tests/xl"
dest_examples = Path(__file__).resolve().parent / "examples"
dest_xl = Path(__file__).resolve().parent / "xl"

# Sync examples folder
print(f"Syncing {source_examples} → {dest_examples}")
copy_dir(source_examples, dest_examples)

# Sync xl folder
copy_dir(source_xl, dest_xl)
