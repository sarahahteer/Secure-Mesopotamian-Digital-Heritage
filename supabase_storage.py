from supabase import create_client
from flask import current_app


def get_supabase_client():
    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError(
            "Supabase URL or secret key is not configured."
        )

    return create_client(url, key)
def upload_encrypted_file(object_path, encrypted_data):
    if not encrypted_data:
        raise ValueError("Encrypted file data is empty.")

    bucket = current_app.config.get("SUPABASE_BUCKET")

    if not bucket:
        raise RuntimeError("Supabase bucket is not configured.")

    client = get_supabase_client()

    return client.storage.from_(bucket).upload(
        path=object_path,
        file=encrypted_data,
        file_options={
            "content-type": "application/octet-stream",
            "upsert": "false"
        }
    )
def delete_stored_file(object_path):
    bucket = current_app.config.get("SUPABASE_BUCKET")

    if not bucket:
        raise RuntimeError("Supabase bucket is not configured.")

    client = get_supabase_client()

    return client.storage.from_(bucket).remove([object_path])

def download_stored_file(object_path):
    if not object_path:
        raise ValueError("Object path is empty.")

    bucket = current_app.config.get("SUPABASE_BUCKET")

    if not bucket:
        raise RuntimeError("Supabase bucket is not configured.")

    client = get_supabase_client()

    return client.storage.from_(bucket).download(object_path)
