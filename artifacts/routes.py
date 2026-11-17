
from pathlib import Path
from io import BytesIO
import hashlib
from flask import send_file, abort
from io import BytesIO
from supabase_storage import download_stored_file
from file_encryption import decrypt_file

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from PIL import Image

from extensions import db
from models import Artifact, MediaFile, AuditLog
from authorization import permission_required, ROLE_PERMISSIONS

from file_validation import validate_image
from file_encryption import encrypt_file, generate_stored_filename
from supabase_storage import upload_encrypted_file, delete_stored_file


artifacts_bp = Blueprint(
    "artifacts",
    __name__,
    url_prefix="/artifacts"
)


@artifacts_bp.get("/")
@permission_required("view")
def index():
    all_artifacts = Artifact.query.order_by(
        Artifact.created_at.desc()
    ).all()

    can_create = "create" in ROLE_PERMISSIONS.get(
        current_user.role, set()
    )

    return render_template(
        "artifacts.html",
        artifacts=all_artifacts,
        can_create=can_create
    )


@artifacts_bp.route("/new", methods=["GET", "POST"])
@permission_required("create")
def create():
    if request.method == "POST":

        inventory_number = request.form.get(
            "inventory_number", ""
        ).strip()

        name_ar = request.form.get(
            "name_ar", ""
        ).strip()

        description_ar = request.form.get(
            "description_ar", ""
        ).strip()

        period = request.form.get("period", "").strip()
        material = request.form.get("material", "").strip()
        discovery_location = request.form.get(
            "discovery_location", ""
        ).strip()

        if not inventory_number or not name_ar:
            flash("Ø±Ù‚Ù… Ø§Ù„Ø¬Ø±Ø¯ ÙˆØ§Ø³Ù… Ø§Ù„Ù‚Ø·Ø¹Ø© Ø­Ù‚ÙˆÙ„ Ù…Ø·Ù„ÙˆØ¨Ø©.", "warning")
            return render_template("artifact_create.html")

        existing = Artifact.query.filter_by(
            inventory_number=inventory_number
        ).first()

        if existing:
            flash("Ø±Ù‚Ù… Ø§Ù„Ø¬Ø±Ø¯ Ù…Ø³ØªØ®Ø¯Ù… Ù…Ø³Ø¨Ù‚Ø§Ù‹.", "danger")
            return render_template("artifact_create.html")

        artifact = Artifact(
            inventory_number=inventory_number,
            name_ar=name_ar,
            description_ar=description_ar or None,
            period=period or None,
            material=material or None,
            discovery_location=discovery_location or None,
            created_by=current_user.id
        )

        quarantine_name = None
        object_path = None

        try:
            db.session.add(artifact)
            db.session.flush()

            uploaded_image = request.files.get("artifact_image")

            if uploaded_image and uploaded_image.filename:

                image_data = uploaded_image.read()
                validate_image(image_data)

                # Verify the image before processing it.
                with Image.open(BytesIO(image_data)) as image:
                    image.verify()

                # Reopen, decode and re-encode to remove original metadata.
                with Image.open(BytesIO(image_data)) as image:
                    if image.width * image.height > 25_000_000:
                        raise ValueError("????? ?????? ????? ????.")

                    image_format = image.format
                    image.load()

                    output = BytesIO()

                    if image_format == "JPEG":
                        image.convert("RGB").save(
                            output, format="JPEG", quality=90, optimize=True
                        )
                        mime_type = "image/jpeg"

                    elif image_format == "PNG":
                        if image.mode not in ("RGB", "RGBA"):
                            image = image.convert("RGBA")
                        image.save(output, format="PNG", optimize=True)
                        mime_type = "image/png"

                    elif image_format == "WEBP":
                        if image.mode not in ("RGB", "RGBA"):
                            image = image.convert("RGBA")
                        image.save(
                            output, format="WEBP", quality=90, method=6
                        )
                        mime_type = "image/webp"

                    else:
                        raise ValueError("???? ?????? ??? ??????.")

                    image_data = output.getvalue()

                original_name = (
                    secure_filename(uploaded_image.filename)[:255]
                    or "artifact-image"
                )

                stored_name = generate_stored_filename()
                object_path = f"artifacts/{artifact.id}/{stored_name}"

                encrypted_data = encrypt_file(image_data)

                upload_encrypted_file(
                    object_path,
                    encrypted_data
                )

                media = MediaFile(
                    artifact_id=artifact.id,
                    original_name=original_name,
                    stored_name=object_path,
                    mime_type=mime_type,
                    sha256=hashlib.sha256(image_data).hexdigest(),
                    encrypted=True,
                    scan_status="validated"
                )

                db.session.add(media)

            log = AuditLog(
                user_id=current_user.id,
                action="create",
                entity_type="artifact",
                entity_id=artifact.id,
                ip_address=request.remote_addr,
                details="ØªÙ…Øª Ø¥Ø¶Ø§ÙØ© Ù‚Ø·Ø¹Ø© Ø£Ø«Ø±ÙŠØ©"
            )

            db.session.add(log)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            if object_path:
                try:
                    delete_stored_file(object_path)
                except Exception:
                    current_app.logger.exception(
                        "Failed to remove uploaded object."
                    )

            flash("ØªØ¹Ø°Ø± Ø­ÙØ¸ Ø§Ù„Ù‚Ø·Ø¹Ø©. Ù‚Ø¯ ÙŠÙƒÙˆÙ† Ø±Ù‚Ù… Ø§Ù„Ø¬Ø±Ø¯ Ù…Ø³ØªØ®Ø¯Ù…Ø§Ù‹.", "danger")
            return render_template("artifact_create.html")

        except Exception:
            db.session.rollback()

            if object_path:
                try:
                    delete_stored_file(object_path)
                except Exception:
                    current_app.logger.exception(
                        "Failed to remove uploaded object."
                    )

            current_app.logger.exception(
                "Artifact creation or image upload failed."
            )

            flash(
                "ØªØ¹Ø°Ø± Ø­ÙØ¸ Ø§Ù„Ù‚Ø·Ø¹Ø© Ø£Ùˆ Ø§Ù„ØµÙˆØ±Ø©. Ù„Ù… ÙŠØªÙ… Ø§Ø¹ØªÙ…Ø§Ø¯ Ø§Ù„ØµÙˆØ±Ø©.",
                "danger"
            )
            return render_template("artifact_create.html")

        finally:
            if quarantine_name:
                quarantine_path = (
                    Path(current_app.config["QUARANTINE_DIR"])
                    / quarantine_name
                )

                try:
                    quarantine_path.unlink(missing_ok=True)
                except OSError:
                    current_app.logger.exception(
                        "Failed to remove quarantine file."
                    )

        flash("ØªÙ…Øª Ø¥Ø¶Ø§ÙØ© Ø§Ù„Ù‚Ø·Ø¹Ø© Ø§Ù„Ø£Ø«Ø±ÙŠØ© Ø¨Ù†Ø¬Ø§Ø­.", "success")
        return redirect(url_for("artifacts.index"))

    return render_template("artifact_create.html")

# Ø¹Ø±Ø¶ ØµÙˆØ±Ø© Ø§Ù„Ù‚Ø·Ø¹Ø© Ø§Ù„Ø£Ø«Ø±ÙŠØ© Ù„Ù„Ù…Ø³ØªØ®Ø¯Ù…ÙŠÙ† Ø§Ù„Ù…ØµØ±Ø­ Ù„Ù‡Ù…
@artifacts_bp.get("/image/<int:media_id>")
@permission_required("view")
def artifact_image(media_id):

    media = MediaFile.query.filter_by(
        id=media_id,
        encrypted=True,
        scan_status="validated"
    ).first_or_404()

    allowed_mime_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if media.mime_type not in allowed_mime_types:
        abort(404)

    try:
        encrypted_data = download_stored_file(
            media.stored_name
        )

        image_data = decrypt_file(encrypted_data)

        response = send_file(
            BytesIO(image_data),
            mimetype=media.mime_type,
            as_attachment=False,
            download_name=media.original_name,
            max_age=0
        )

        response.headers["Cache-Control"] = "private, no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"

        return response

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve artifact image."
        )
        abort(404)

