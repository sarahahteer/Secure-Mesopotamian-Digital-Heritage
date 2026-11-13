
from getpass import getpass
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    if User.query.filter_by(role="admin").first():
        print("An admin account already exists.")
    else:
        print("=== Create First Administrator ===")

        username = input("Admin username: ").strip()
        email = input("Admin email: ").strip()

        password = getpass("Admin password: ")
        confirm_password = getpass("Confirm password: ")

        if len(username) < 4:
            raise SystemExit("Username must be at least 4 characters.")

        if "@" not in email or "." not in email:
            raise SystemExit("Please enter a valid email address.")

        if len(password) < 12:
            raise SystemExit("Password must be at least 12 characters.")

        if password != confirm_password:
            raise SystemExit("Passwords do not match.")

        if User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            raise SystemExit("Username or email already exists.")

        admin = User(
            username=username,
            email=email,
            role="admin",
            is_active=True
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Administrator account created successfully.")
