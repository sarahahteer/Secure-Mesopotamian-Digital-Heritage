
import secrets
import hashlib
from datetime import timedelta

from models import UserInvitation, utcnow
from extensions import db


INVITATION_HOURS = 24


def generate_invitation(username, role, created_by):
    """
    إنشاء دعوة عشوائية صالحة لمدة 24 ساعة.
    """

    allowed_roles = {
        "assistant_admin",
        "researcher",
        "senior_researcher"
    }

    if role not in allowed_roles:
        raise ValueError("Invalid invitation role")

    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    invitation = UserInvitation(
        username=username,
        role=role,
        token_hash=token_hash,
        expires_at=utcnow() + timedelta(
            hours=INVITATION_HOURS
        ),
        created_by=created_by
    )

    db.session.add(invitation)

    return invitation, token


def hash_invitation_token(token):
    """
    تحويل رمز الدعوة إلى SHA-256 للتحقق منه.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
