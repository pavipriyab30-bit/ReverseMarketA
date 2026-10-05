from dataclasses import dataclass
from typing import Optional


@dataclass
class Provider:
    """Represents a BESTORA FIT service provider."""

    id: Optional[int]
    name: str
    category: str
    description: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    experience_years: int
    rating: float
    review_count: int
    completed_jobs: int
    response_rate: float
    verified: bool
    trust_score: float

    @classmethod
    def from_row(cls, row):
        """Create a Provider object from a SQLite row."""

        return cls(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            description=row["description"],
            location=row["location"],
            phone=row["phone"],
            email=row["email"],
            experience_years=row["experience_years"],
            rating=row["rating"],
            review_count=row["review_count"],
            completed_jobs=row["completed_jobs"],
            response_rate=row["response_rate"],
            verified=bool(row["verified"]),
            trust_score=row["trust_score"],
        )

    def to_dict(self):
        """Convert the provider into a dictionary."""

        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "location": self.location,
            "phone": self.phone,
            "email": self.email,
            "experience_years": self.experience_years,
            "rating": self.rating,
            "review_count": self.review_count,
            "completed_jobs": self.completed_jobs,
            "response_rate": self.response_rate,
            "verified": self.verified,
            "trust_score": self.trust_score,
        } 