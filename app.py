import os
from flask import Flask, render_template, request
from config import Config
from extensions import db, login_manager, csrf, limiter
from models import User, Artifact, ArchaeologicalSite, Manuscript
from auth.routes import auth_bp
from authorization import permission_required


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["QUARANTINE_DIR"], exist_ok=True)
    os.makedirs(app.config["ENCRYPTED_UPLOAD_DIR"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # إعدادات جلسات تسجيل الدخول
    login_manager.session_protection = "strong"
    login_manager.login_view = "auth.login"
    login_manager.login_message = "يرجى تسجيل الدخول أولاً."
    login_manager.login_message_category = "warning"

    # تسجيل مسارات المصادقة
    app.register_blueprint(auth_bp)

    # تسجيل مسارات إدارة المستخدمين
    from admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    @app.get("/")
    @permission_required("view")
    def home():
        stats = {
            "users": User.query.count(),
            "artifacts": Artifact.query.count(),
            "sites": ArchaeologicalSite.query.count(),
            "manuscripts": Manuscript.query.count(),
        }

        return render_template("dashboard.html", stats=stats)

    @app.get("/artifacts")
    @permission_required("view")
    def artifacts():
        return render_template(
            "section.html",
            title="القطع الأثرية",
            description="أرشيف القطع الأثرية العراقية وتوثيق بياناتها العلمية.",
            section="artifacts"
        )

    @app.get("/sites")
    @permission_required("view")
    def sites():
        return render_template(
            "section.html",
            title="المواقع الأثرية",
            description="توثيق المواقع الأثرية ومعلوماتها الجغرافية والتاريخية.",
            section="sites"
        )

    @app.get("/manuscripts")
    @permission_required("view")
    def manuscripts():
        return render_template(
            "section.html",
            title="المخطوطات والوثائق التاريخية",
            description="أرشفة المخطوطات والوثائق التاريخية وحفظ بياناتها.",
            section="manuscripts"
        )

    @app.get("/search")
    @permission_required("view")
    def search():
        query = request.args.get("q", "").strip()
        return render_template(
            "section.html",
            title="البحث في الأرشيف",
            description=f"نتائج البحث عن: {query}" if query else "أدخل عبارة للبحث في الأرشيف.",
            section="search",
            query=query
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    create_app().run()