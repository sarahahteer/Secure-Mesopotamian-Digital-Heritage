from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="researcher")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    # Ø§Ù„Ø¹Ù„Ø§Ù‚Ø§Øª Ø§Ù„Ø¹ÙƒØ³ÙŠØ© (Ø§Ø®ØªÙŠØ§Ø±ÙŠ Ù„ÙƒÙ† Ù…ÙÙŠØ¯ Ø¬Ø¯Ø§Ù‹ Ù„Ù„ÙˆØµÙˆÙ„ Ù„Ù„Ø¨ÙŠØ§Ù†Ø§Øª Ø¨Ø³Ù‡ÙˆÙ„Ø©)
    invitations = db.relationship("UserInvitation", back_populates="creator", lazy="select")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Artifact(db.Model):
    __tablename__ = "artifacts"

    id = db.Column(db.Integer, primary_key=True)
    inventory_number = db.Column(db.String(100), unique=True, nullable=False)
    name_ar = db.Column(db.String(250), nullable=False)
    description_ar = db.Column(db.Text)
    period = db.Column(db.String(150))
    material = db.Column(db.String(150))
    discovery_location = db.Column(db.String(250))
    status = db.Column(db.String(30), nullable=False, default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    media_files = db.relationship(
        "MediaFile",
        back_populates="artifact",
        lazy="select"
    )

class ArchaeologicalSite(db.Model):
    __tablename__ = "archaeological_sites"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(250), nullable=False)
    governorate = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    period = db.Column(db.String(150))
    description_ar = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class Manuscript(db.Model):
    __tablename__ = "manuscripts"

    id = db.Column(db.Integer, primary_key=True)
    archive_number = db.Column(db.String(100), unique=True, nullable=False)
    title_ar = db.Column(db.String(250), nullable=False)
    language = db.Column(db.String(80))
    estimated_date = db.Column(db.String(150))
    repository = db.Column(db.String(250))
    description_ar = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class MediaFile(db.Model):
    __tablename__ = "media_files"

    id = db.Column(db.Integer, primary_key=True)
    artifact_id = db.Column(db.Integer, db.ForeignKey("artifacts.id"), nullable=True, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), unique=True, nullable=False)
    mime_type = db.Column(db.String(120))
    sha256 = db.Column(db.String(64), nullable=False)
    encrypted = db.Column(db.Boolean, nullable=False, default=False)
    scan_status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    artifact = db.relationship(
        "Artifact",
        back_populates="media_files"
    )

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(80))
    entity_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    details = db.Column(db.Text)

class SecurityEvent(db.Model):
    __tablename__ = "security_events"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="info")
    source_ip = db.Column(db.String(45))
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

class UserInvitation(db.Model):
    __tablename__ = "user_invitations"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True) # ØªØ®Ø²ÙŠÙ† SHA-256 Ù„Ù„Ø±Ù…Ø²
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    # Ø§Ù„Ø¹Ù„Ø§Ù‚Ø© Ø§Ù„Ø¹ÙƒØ³ÙŠØ© Ù…Ø¹ Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…ÙŠÙ†
    creator = db.relationship("User", back_populates="invitations")
