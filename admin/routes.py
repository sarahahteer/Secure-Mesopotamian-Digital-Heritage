from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from extensions import db
from models import User, AuditLog, UserInvitation, utcnow
from authorization import permission_required, permission_required_any
from invitations import generate_invitation

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/users")
@permission_required("manage_system")
def users():
    all_users = User.query.order_by(User.id.asc()).all()

    return render_template(
        "admin/users.html",
        users=all_users
    )


@admin_bp.get("/researchers")
@permission_required_any("manage_researchers")
def researchers():
    allowed_roles = {"researcher", "senior_researcher"}

    researchers_list = User.query.filter(
        User.role.in_(allowed_roles)
    ).order_by(User.id.asc()).all()

    return render_template(
        "admin/users.html",
        users=researchers_list,
        researchers_only=True
    )


@admin_bp.post("/researchers/<int:user_id>/update")
@permission_required_any("manage_researchers")
def update_researcher(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    allowed_roles = {"researcher", "senior_researcher"}

    # منع تعديل أي حساب ليس باحثاً
    if user.role not in allowed_roles:
        abort(403)

    new_role = request.form.get("role", "").strip()
    active_value = request.form.get("is_active", "")

    if new_role not in allowed_roles:
        abort(400)

    if active_value not in {"0", "1"}:
        abort(400)

    old_role = user.role
    old_active = user.is_active

    user.role = new_role
    user.is_active = active_value == "1"

    try:
        audit = AuditLog(
            user_id=current_user.id,
            action="update_researcher",
            entity_type="User",
            entity_id=user.id,
            ip_address=request.remote_addr,
            details=(
                f"role: {old_role} -> {new_role}; "
                f"is_active: {old_active} -> {user.is_active}"
            )
        )

        db.session.add(audit)
        db.session.commit()

        flash("تم تحديث حساب الباحث بنجاح.", "success")

    except Exception:
        db.session.rollback()
        flash("حدث خطأ أثناء تحديث حساب الباحث.", "danger")

    return redirect(url_for("admin.researchers"))


@admin_bp.post("/users/<int:user_id>/update")
@permission_required("manage_system")
def update_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        abort(404)

    if user.id == current_user.id:
        flash("لا يمكنك تعديل حسابك من هذه الصفحة.", "warning")
        return redirect(url_for("admin.users"))

    allowed_roles = {"researcher", "senior_researcher"}

    if user.role not in allowed_roles:
        flash("لا يمكن تعديل حسابات المديرين من هذه الصفحة.", "danger")
        return redirect(url_for("admin.users"))

    new_role = request.form.get("role", "").strip()
    active_value = request.form.get("is_active", "")

    if new_role not in allowed_roles:
        flash("الدور المحدد غير صالح.", "danger")
        return redirect(url_for("admin.users"))

    if active_value not in {"0", "1"}:
        flash("حالة الحساب غير صالحة.", "danger")
        return redirect(url_for("admin.users"))

    old_role = user.role
    old_active = user.is_active

    user.role = new_role
    user.is_active = active_value == "1"

    try:
        audit = AuditLog(
            user_id=current_user.id,
            action="update_user",
            entity_type="User",
            entity_id=user.id,
            ip_address=request.remote_addr,
            details=(
                f"role: {old_role} -> {new_role}; "
                f"is_active: {old_active} -> {user.is_active}"
            )
        )

        db.session.add(audit)
        db.session.commit()

        flash("تم تحديث بيانات المستخدم بنجاح.", "success")

    except Exception:
        db.session.rollback()
        flash("حدث خطأ أثناء تحديث المستخدم.", "danger")

    return redirect(url_for("admin.users"))


@admin_bp.route("/invitations/new", methods=["GET", "POST"])
@permission_required_any("manage_researchers")
def create_invitation():

    # تحديد الأدوار المسموح بإنشاء دعوات لها
    if current_user.role == "super_admin":
        allowed_roles = {
            "assistant_admin",
            "researcher",
            "senior_researcher"
        }

    elif current_user.role == "assistant_admin":
        allowed_roles = {
            "researcher",
            "senior_researcher"
        }

    else:
        abort(403)

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        role = request.form.get("role", "").strip()

        if not username or not role:
            flash("يرجى ملء جميع الحقول.", "warning")
            return redirect(url_for("admin.create_invitation"))

        if (
            len(username) < 3
            or len(username) > 80
            or any(char.isspace() for char in username)
        ):
            flash("اسم المستخدم يجب أن يكون بين 3 و80 حرفاً دون مسافات.", "danger")
            return redirect(url_for("admin.create_invitation"))

        if role not in allowed_roles:
            abort(403)

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("اسم المستخدم مستخدم مسبقاً.", "danger")
            return redirect(url_for("admin.create_invitation"))

        active_invitation = UserInvitation.query.filter(
            UserInvitation.username == username,
            UserInvitation.used_at.is_(None),
            UserInvitation.expires_at > utcnow()
        ).first()

        if active_invitation:
            flash("توجد دعوة فعالة لهذا الاسم بالفعل.", "warning")
            return redirect(url_for("admin.create_invitation"))

        try:
            invitation, token = generate_invitation(
                username=username,
                role=role,
                created_by=current_user.id
            )

            db.session.flush()

            audit = AuditLog(
                user_id=current_user.id,
                action="create_invitation",
                entity_type="UserInvitation",
                entity_id=invitation.id,
                ip_address=request.remote_addr,
                details=f"Invitation created for {username}, role={role}"
            )

            db.session.add(audit)
            db.session.commit()

            # عرض الرمز مرة واحدة في نتيجة الطلب
            return render_template(
                "admin/invitation_created.html",
                invitation=invitation,
                token=token
            )

        except Exception:
            db.session.rollback()
            flash("حدث خطأ أثناء إنشاء الدعوة.", "danger")
            return redirect(url_for("admin.create_invitation"))

    return render_template(
        "admin/create_invitation.html",
        allowed_roles=allowed_roles
    )