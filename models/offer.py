from dataclasses import dataclass
from typing import Optional


@dataclass
class Offer:
    """Represents a service offer from a BESTORA FIT provider."""

    id: Optional[int]
    provider_id: int
    title: str
    description: Optional[str]
    category: str
    price: float
    currency: str
    delivery_time: Optional[str]
    availability: str
    rating: float

    @classmethod
    def from_row(cls, row):
        """Create an Offer object from a SQLite row."""

        return cls(
            id=row["id"],
            provider_id=row["provider_id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            price=float(row["price"]),
            currency=row["currency"],
            delivery_time=row["delivery_time"],
            availability=row["availability"],
            rating=float(row["rating"]),
        )

    def to_dict(self):
        """Convert the offer into a dictionary."""

        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "delivery_time": self.delivery_time,
            "availability": self.availability,
            "rating": self.rating,
        } 