import sqlite3
import sys
from pathlib import Path


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from config import config


PRODUCTS = [
    {
        "name": "Galaxy A55 5G",
        "brand": "Samsung",
        "category": "Smartphone",
        "description": (
            "5G smartphone with AMOLED display, strong battery life, "
            "good camera system and 8GB RAM."
        ),
        "price": 32999.0,
        "rating": 4.5,
        "review_count": 1840,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/samsung-a55",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "Nord CE 4 5G",
        "brand": "OnePlus",
        "category": "Smartphone",
        "description": (
            "5G smartphone with AMOLED display, fast charging, "
            "large battery and 8GB RAM."
        ),
        "price": 24999.0,
        "rating": 4.4,
        "review_count": 1520,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/oneplus-nord-ce4",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "iPhone 15",
        "brand": "Apple",
        "category": "Smartphone",
        "description": (
            "Premium smartphone with advanced camera system, "
            "strong performance and Super Retina display."
        ),
        "price": 59999.0,
        "rating": 4.7,
        "review_count": 3200,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/iphone-15",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "IdeaPad Slim 3",
        "brand": "Lenovo",
        "category": "Laptop",
        "description": (
            "Everyday laptop with Intel processor, 15.6-inch display, "
            "16GB RAM and SSD storage."
        ),
        "price": 45999.0,
        "rating": 4.3,
        "review_count": 980,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/lenovo-ideapad",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "Vivobook 15",
        "brand": "ASUS",
        "category": "Laptop",
        "description": (
            "Slim laptop with Intel processor, Full HD display, "
            "16GB RAM and SSD storage."
        ),
        "price": 48999.0,
        "rating": 4.4,
        "review_count": 1120,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/asus-vivobook",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "MacBook Air M2",
        "brand": "Apple",
        "category": "Laptop",
        "description": (
            "Lightweight laptop powered by Apple M2 chip with "
            "excellent battery life and fast SSD storage."
        ),
        "price": 74999.0,
        "rating": 4.8,
        "review_count": 2100,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/macbook-air-m2",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "WH-1000XM5",
        "brand": "Sony",
        "category": "Headphones",
        "description": (
            "Wireless over-ear headphones with active noise "
            "cancellation, premium sound and long battery life."
        ),
        "price": 29999.0,
        "rating": 4.7,
        "review_count": 1750,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/sony-xm5",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "AirPods Pro 2",
        "brand": "Apple",
        "category": "Headphones",
        "description": (
            "Wireless earbuds with active noise cancellation, "
            "transparency mode and spatial audio."
        ),
        "price": 24999.0,
        "rating": 4.6,
        "review_count": 2600,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/airpods-pro",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "Smart LED TV 43",
        "brand": "LG",
        "category": "Television",
        "description": (
            "43-inch 4K smart television with HDR, streaming apps "
            "and built-in Wi-Fi."
        ),
        "price": 32999.0,
        "rating": 4.5,
        "review_count": 1450,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/lg-tv-43",
        "image_url": "",
        "availability": "available",
    },
    {
        "name": "4K Smart TV 43",
        "brand": "Samsung",
        "category": "Television",
        "description": (
            "43-inch 4K smart television with HDR, streaming apps, "
            "Wi-Fi and modern slim design."
        ),
        "price": 34999.0,
        "rating": 4.6,
        "review_count": 1680,
        "seller": "BESTORA Store",
        "product_url": "https://example.com/samsung-tv-43",
        "image_url": "",
        "availability": "available",
    },
]


def seed_products():
    """Insert the initial BESTORA FIT Product Mode catalogue."""

    database_path = PROJECT_ROOT / config.DATABASE_PATH

    connection = sqlite3.connect(database_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Product Mode owns this table, so replacing the catalogue
        # is safe and does not affect Service Mode tables.
        connection.execute("DELETE FROM products")

        for product in PRODUCTS:
            connection.execute(
                """
                INSERT INTO products (
                    name,
                    brand,
                    category,
                    description,
                    price,
                    currency,
                    rating,
                    review_count,
                    seller,
                    product_url,
                    image_url,
                    availability
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["name"],
                    product["brand"],
                    product["category"],
                    product["description"],
                    product["price"],
                    "INR",
                    product["rating"],
                    product["review_count"],
                    product["seller"],
                    product["product_url"],
                    product["image_url"],
                    product["availability"],
                ),
            )

        connection.commit()

        print(
            f"Seeded {len(PRODUCTS)} Product Mode products."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    seed_products() 