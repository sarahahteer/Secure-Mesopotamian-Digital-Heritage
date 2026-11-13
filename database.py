"""Initialize schema for local development. Use Flask-Migrate for later changes."""
from app import create_app
from extensions import db
import models  # noqa: F401 - registers model metadata

app = create_app()
with app.app_context():
    db.create_all()
    print("PostgreSQL schema created/verified.")
