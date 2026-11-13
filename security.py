import hashlib
from extensions import db
from models import AuditLog

def sha256_file(file_stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: file_stream.read(1024 * 1024), b""):
        digest.update(chunk)
    file_stream.seek(0)
    return digest.hexdigest()

def record_audit(user_id, action, entity_type=None, entity_id=None, ip_address=None, details=None):
    db.session.add(AuditLog(
        user_id=user_id, action=action, entity_type=entity_type,
        entity_id=entity_id, ip_address=ip_address, details=details
    ))
    db.session.commit()
