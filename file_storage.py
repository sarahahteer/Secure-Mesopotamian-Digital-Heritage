
import secrets
from pathlib import Path
from flask import current_app


def save_to_quarantine(file_data):
    if not file_data:
        raise ValueError("لا يمكن حفظ ملف فارغ.")

    quarantine_dir = Path(
        current_app.config["QUARANTINE_DIR"]
    ).resolve()

    quarantine_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = secrets.token_hex(32) + ".upload"
    file_path = quarantine_dir / filename

    try:
        with file_path.open("xb") as file:
            file.write(file_data)
            file.flush()

    except OSError:
        if file_path.exists():
            file_path.unlink()
        raise

    return filename
