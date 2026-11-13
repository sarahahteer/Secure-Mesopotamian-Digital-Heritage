
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from werkzeug.security import generate_password_hash
from extensions import db, limiter
from models import User, UserInvitation, AuditLog, utcnow
from invitations import hash_invitation_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # مثال على استخدام or_ إذا أردت السماح بالبحث باسم المستخدم أو البريد الإلكتروني (إن وجد استعلام تسجيل هنا)
        existing_user = User.query.filter(
            or_(
                User.username == username,
                User.email == username  # أو email إذا كان الحقل متاحاً
            )
        ).first()

        user = User.query.filter_by(username=username).first()

        if user and user.is_active and user.check_password(password):
            login_user(user)
            flash("تم تسجيل الدخول بنجاح.", "success")
            return redirect(url_for("home"))

        flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():

    if current_user.is_authenticated:
        logout_user()
        flash("تم تسجيل الخروج بنجاح.", "success")

    return redirect(url_for("auth.login"))

@auth_bp.route("/activate", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def activate():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        token = request.form.get("token", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # التحقق من الحقول المطلوبة
        if not all([username, token, email, password, confirm_password]):
            flash("يرجى ملء جميع الحقول.", "danger")
            return redirect(url_for("auth.activate"))

        # التحقق من طول كلمة المرور
        if len(password) < 12:
            flash("يجب أن تتكون كلمة المرور من 12 حرفاً على الأقل.", "danger")
            return redirect(url_for("auth.activate"))

        if password != confirm_password:
            flash("كلمتا المرور غير متطابقتين.", "danger")
            return redirect(url_for("auth.activate"))

        # التحقق من صيغة البريد الإلكتروني بشكل أولي
        if "@" not in email or "." not in email.split("@")[-1]:
            flash("يرجى إدخال بريد إلكتروني صحيح.", "danger")
            return redirect(url_for("auth.activate"))

        # البحث عن الدعوة باستخدام بصمة الرمز
        token_hash = hash_invitation_token(token)

        invitation = UserInvitation.query.filter_by(
            token_hash=token_hash,
            username=username
        ).with_for_update().first()

        if not invitation:
            flash("رمز الدعوة أو اسم المستخدم غير صحيح.", "danger")
            return redirect(url_for("auth.activate"))

        # التحقق من عدم استخدام الدعوة وانتهاء صلاحيتها
        if invitation.used_at is not None:
            flash("تم استخدام هذه الدعوة مسبقاً.", "danger")
            return redirect(url_for("auth.activate"))

        if invitation.expires_at <= utcnow():
            flash("انتهت صلاحية الدعوة. يرجى طلب دعوة جديدة.", "danger")
            return redirect(url_for("auth.activate"))

        # التحقق من الدور
        allowed_roles = {
            "assistant_admin",
            "researcher",
            "senior_researcher"
        }

        if invitation.role not in allowed_roles:
            flash("نوع الدعوة غير صالح.", "danger")
            return redirect(url_for("auth.activate"))

        # منع تكرار اسم المستخدم أو البريد الإلكتروني
        if User.query.filter_by(username=username).first():
            flash("اسم المستخدم مستخدم بالفعل.", "danger")
            return redirect(url_for("auth.activate"))

        if User.query.filter_by(email=email).first():
            flash("البريد الإلكتروني مستخدم بالفعل.", "danger")
            return redirect(url_for("auth.activate"))

        try:
            user = User(
                username=username,
                email=email,
                role=invitation.role,
                is_active=True
            )
            user.set_password(password)

            db.session.add(user)
            db.session.flush()

            invitation.used_at = utcnow()

            audit = AuditLog(
                user_id=user.id,
                action="activate_invitation",
                entity_type="User",
                entity_id=user.id,
                ip_address=request.remote_addr,
                details=f"Account activated: {username}"
            )

            db.session.add(audit)
            db.session.commit()

            flash("تم تفعيل حسابك بنجاح. يمكنك تسجيل الدخول الآن.", "success")
            return redirect(url_for("auth.login"))

        except Exception:
            db.session.rollback()
            flash("حدث خطأ أثناء تفعيل الحساب. يرجى المحاولة مرة أخرى.", "danger")
            return redirect(url_for("auth.activate"))

    return render_template("activate.html")
