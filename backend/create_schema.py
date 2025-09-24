import os
from app import app, db


def main() -> None:
    # If DATABASE_URL is provided, app.py will already pick it up via config.py
    # Just ensure we run within the app context and create all tables.
    with app.app_context():
        db.create_all()
        print("Schema created (or already exists).")


if __name__ == "__main__":
    main()


