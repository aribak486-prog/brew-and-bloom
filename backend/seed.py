"""Insert example catalog entries and local demo users."""
import os

from dotenv import load_dotenv
from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User, UserRole

load_dotenv()

CATEGORIES = [
    ("Coffee", "Espresso favorites, slow brews and cozy classics.", "https://images.unsplash.com/photo-1442512595331-e89e73853f31"),
    ("Pastries", "Flaky, buttery bakes, made fresh each morning.", "https://images.unsplash.com/photo-1555507036-ab1f4038808a"),
    ("Desserts", "Little celebrations, one sweet bite at a time.", "https://images.unsplash.com/photo-1578985545062-69928b1d9587"),
    ("Cold Drinks", "Iced coffee, matcha and cool afternoon sips.", "https://images.unsplash.com/photo-1461023058943-07fcbe16d735"),
]
ITEMS = [
    ("Caramel Latte", "Espresso, steamed milk and house caramel.", 5.50, 4.9, "Coffee", "photo-1461023058943-07fcbe16d735"),
    ("Classic Cappuccino", "Rich espresso with silky steamed milk foam.", 4.80, 4.8, "Coffee", "photo-1570968915860-54d5c301fa9f"),
    ("Strawberry Cheesecake", "Vanilla cheesecake, berry compote and buttery crumb.", 6.20, 5.0, "Desserts", "photo-1533134242443-d4fd215305ad"),
    ("Iced Matcha", "Ceremonial matcha, oat milk and a little honey.", 5.00, 4.9, "Cold Drinks", "photo-1515823064-d6e0c04616a7"),
    ("Chocolate Croissant", "Flaky, golden layers filled with dark chocolate.", 3.80, 4.9, "Pastries", "photo-1555507036-ab1f4038808a"),
    ("Mocha Frappe", "Cold brew blended with cocoa and a little cream.", 5.80, 4.8, "Cold Drinks", "photo-1461023058943-07fcbe16d735"),
]


def ensure_user(db, name: str, email: str, password: str, role: UserRole) -> None:
    if db.scalar(select(User).where(User.email == email)) is None:
        db.add(User(name=name, email=email, password_hash=hash_password(password), role=role))


def main() -> None:
    with SessionLocal() as db:
        categories = {}
        for name, description, image in CATEGORIES:
            category = db.scalar(select(Category).where(Category.name == name))
            if category is None:
                category = Category(name=name, description=description, image=f"{image}?auto=format&fit=crop&w=800&q=85")
                db.add(category)
                db.flush()
            categories[name] = category
        for name, description, price, rating, category_name, image in ITEMS:
            if db.scalar(select(MenuItem).where(MenuItem.name == name)) is None:
                db.add(MenuItem(name=name, description=description, price=price, rating=rating, category_id=categories[category_name].id,
                                image=f"https://images.unsplash.com/{image}?auto=format&fit=crop&w=900&q=85", available=True))
        admin_password = os.getenv("DEMO_ADMIN_PASSWORD", "")
        customer_password = os.getenv("DEMO_CUSTOMER_PASSWORD", "")
        if admin_password:
            ensure_user(db, "Brew & Bloom Admin", "admin@brewandbloom.local", admin_password, UserRole.ADMIN)
        if customer_password:
            ensure_user(db, "Demo Customer", "customer@brewandbloom.local", customer_password, UserRole.CUSTOMER)
        db.commit()
    print("Seed complete. Optional demo users are created only when their password environment variables are set.")


if __name__ == "__main__":
    main()
