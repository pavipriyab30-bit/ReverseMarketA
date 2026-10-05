from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """Represents a product in BESTORA FIT Product Mode."""

    id: Optional[int]
    name: str
    brand: Optional[str]
    category: Optional[str]
    description: Optional[str]
    price: Optional[float]
    currency: str
    rating: float
    review_count: int
    seller: Optional[str]
    product_url: Optional[str]
    image_url: Optional[str]
    availability: str

    @classmethod
    def from_row(cls, row):
        """Create a Product object from a SQLite row."""

        return cls(
            id=row["id"],
            name=row["name"],
            brand=row["brand"],
            category=row["category"],
            description=row["description"],
            price=float(row["price"]) if row["price"] is not None else None,
            currency=row["currency"],
            rating=float(row["rating"]),
            review_count=row["review_count"],
            seller=row["seller"],
            product_url=row["product_url"],
            image_url=row["image_url"],
            availability=row["availability"],
        )

    def to_dict(self):
        """Convert the product into a dictionary."""

        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "rating": self.rating,
            "review_count": self.review_count,
            "seller": self.seller,
            "product_url": self.product_url,
            "image_url": self.image_url,
            "availability": self.availability,
        } 