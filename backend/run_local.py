"""Start a self-contained local backend using SQLite for cafe development."""
import os
import secrets

# This override lets the website's API run locally even when PostgreSQL is not installed.
os.environ["DATABASE_URL"] = "sqlite:///./brew_bloom_local.db"
os.environ["BREW_BLOOM_OFFLINE_CHAT"] = "1"
if len(os.environ.get("JWT_SECRET_KEY", "").strip()) < 32 or os.environ.get("JWT_SECRET_KEY", "").startswith("replace-this"):
    os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)

import uvicorn
from sqlalchemy import select

import app.models  # noqa: F401 - register all models with SQLAlchemy metadata
from app.database.connection import Base, SessionLocal, engine
from app.models.category import Category
from seed import main as seed_demo_data


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        has_catalog = db.scalar(select(Category.id).limit(1)) is not None
    if not has_catalog:
        seed_demo_data()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
