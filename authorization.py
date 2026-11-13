from functools import wraps
from flask import abort
from flask_login import current_user, login_required, logout_user


ROLE_PERMISSIONS = {
    "visitor": {
        "view"
    },

    "researcher": {
        "view", "create", "upload"
    },

    "senior_researcher": {
        "view", "create", "upload", "edit", "review"
    },

    # المدير المساعد: إدارة حسابات الباحثين فقط
    "assistant_admin": {
        "view", "manage_researchers"
    },

    # المدير الإداري
    "admin": {
        "view", "create", "upload", "edit",
        "review", "publish", "manage_users", "view_logs"
    },

    # المدير الأعلى (تمت إضافة manage_researchers هنا)
    "super_admin": {
        "view", "create", "upload", "edit",
        "review", "publish", "delete",
        "manage_users", "manage_researchers",
        "view_logs", "manage_system"
    }
}


def permission_required(permission):
    def decorator(view):

        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):

            if not current_user.is_active:
                logout_user()
                abort(403)

            user_permissions = ROLE_PERMISSIONS.get(
                current_user.role, set()
            )

            if permission not in user_permissions:
                abort(403)

            return view(*args, **kwargs)

        return wrapped

    return decorator


def permission_required_any(*permissions):
    def decorator(view):

        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):

            if not current_user.is_active:
                logout_user()
                abort(403)

            user_permissions = ROLE_PERMISSIONS.get(
                current_user.role, set()
            )

            if not any(p in user_permissions for p in permissions):
                abort(403)

            return view(*args, **kwargs)

        return wrapped

    return decorator