from typing import Any, Dict, List

from config import config
from database.database import get_database
from models.offer import Offer
from models.provider import Provider
from services.risk_engine import risk_engine
from services.trust_engine import trust_engine


class MatchingEngine:
    """
    Match service requirements against providers and offers.

    Matching priority:
        1. Category compatibility
        2. Budget fit
        3. Location fit
        4. Availability
        5. Trust
        6. Rating
        7. Risk penalty

    Providers from an unrelated service category are excluded
    before ranking.
    """

    CATEGORY_WEIGHT = 30
    BUDGET_WEIGHT = 20
    LOCATION_WEIGHT = 10
    AVAILABILITY_WEIGHT = 10
    TRUST_WEIGHT = 20
    RATING_WEIGHT = 10

    def find_matches(
        self,
        requirement: Dict[str, Any],
        limit: int = None,
    ) -> List[Dict[str, Any]]:

        if limit is None:
            limit = config.DEFAULT_MATCH_LIMIT

        limit = max(1, min(int(limit), 50))

        category = self._normalize(
            requirement.get("category")
        )

        location = self._normalize(
            requirement.get("location")
        )

        budget_min = self._to_float(
            requirement.get("budget_min")
        )

        budget_max = self._to_float(
            requirement.get("budget_max")
        )

        preferred_date = self._normalize(
            requirement.get("preferred_date")
        )

        connection = get_database()

        try:
            rows = connection.execute(
                """
                SELECT
                    p.*,
                    o.id AS offer_id,
                    o.provider_id AS offer_provider_id,
                    o.title AS offer_title,
                    o.description AS offer_description,
                    o.category AS offer_category,
                    o.price AS offer_price,
                    o.currency AS offer_currency,
                    o.delivery_time AS offer_delivery_time,
                    o.availability AS offer_availability,
                    o.rating AS offer_rating
                FROM providers p
                JOIN offers o
                    ON o.provider_id = p.id
                ORDER BY p.id, o.id
                """
            ).fetchall()

        finally:
            connection.close()

        matches: List[Dict[str, Any]] = []

        for row in rows:

            provider = Provider.from_row(row)

            offer = Offer(
                id=row["offer_id"],
                provider_id=row["offer_provider_id"],
                title=row["offer_title"],
                description=row["offer_description"],
                category=row["offer_category"],
                price=row["offer_price"],
                currency=row["offer_currency"],
                delivery_time=row["offer_delivery_time"],
                availability=row["offer_availability"],
                rating=row["offer_rating"],
            )

            # -------------------------------------------------
            # HARD CATEGORY FILTER
            # -------------------------------------------------
            #
            # If the user asks for a specific service category,
            # unrelated providers must not enter the ranking.
            #
            if category:
                provider_category = self._normalize(
                    provider.category
                )

                offer_category = self._normalize(
                    offer.category
                )

                category_match = (
                    self._category_matches(
                        category,
                        provider_category,
                    )
                    or
                    self._category_matches(
                        category,
                        offer_category,
                    )
                )

                if not category_match:
                    continue

            # -------------------------------------------------
            # COMPONENT SCORES
            # -------------------------------------------------

            category_score = self._category_score(
                requirement_category=category,
                provider_category=provider.category,
                offer_category=offer.category,
            )

            budget_score = self._budget_score(
                budget_min=budget_min,
                budget_max=budget_max,
                offer_price=offer.price,
            )

            location_score = self._location_score(
                requirement_location=location,
                provider_location=provider.location,
            )

            availability_score = self._availability_score(
                preferred_date=preferred_date,
                availability=offer.availability,
            )

            trust_score = trust_engine.calculate_score(
                provider
            )

            rating_score = self._rating_score(
                provider.rating
            )

            # -------------------------------------------------
            # RISK
            # -------------------------------------------------

            risk_result = risk_engine.analyze(
                provider,
                offer,
            )

            risk_score = risk_result["risk_score"]

            risk_penalty = min(
                risk_score * 0.20,
                20,
            )

            # -------------------------------------------------
            # FINAL MATCH SCORE
            # -------------------------------------------------

            raw_score = (
                category_score * 0.30
                + budget_score * 0.20
                + location_score * 0.10
                + availability_score * 0.10
                + trust_score * 0.20
                + rating_score * 0.10
            )

            match_score = max(
                0,
                min(
                    100,
                    raw_score - risk_penalty,
                ),
            )

            trust_level = trust_engine.get_trust_level(
                trust_score
            )

            recommendation_reason = (
                self._build_recommendation_reason(
                    category_score=category_score,
                    budget_score=budget_score,
                    location_score=location_score,
                    availability_score=availability_score,
                    trust_score=trust_score,
                    rating_score=rating_score,
                    risk_score=risk_score,
                )
            )

            matches.append(
                {
                    "provider": provider.to_dict(),
                    "offer": offer.to_dict(),
                    "match_score": round(match_score, 1),

                    "category_score": round(
                        category_score,
                        1,
                    ),

                    "budget_score": round(
                        budget_score,
                        1,
                    ),

                    "location_score": round(
                        location_score,
                        1,
                    ),

                    "availability_score": round(
                        availability_score,
                        1,
                    ),

                    "trust_score": round(
                        trust_score,
                        1,
                    ),

                    "rating_score": round(
                        rating_score,
                        1,
                    ),

                    "trust_level": trust_level,

                    "risk_score": risk_score,

                    "risk_level": risk_result[
                        "risk_level"
                    ],

                    "risk_alerts": risk_result[
                        "alerts"
                    ],

                    "safe_to_recommend": risk_result[
                        "safe_to_recommend"
                    ],

                    "recommendation_reason":
                        recommendation_reason,
                }
            )

        # Highest match first.
        matches.sort(
            key=lambda item: item["match_score"],
            reverse=True,
        )

        return matches[:limit]

    # =========================================================
    # CATEGORY
    # =========================================================

    @staticmethod
    def _category_matches(
        requirement_category: str,
        provider_category: str,
    ) -> bool:

        requirement_category = (
            MatchingEngine._normalize(
                requirement_category
            )
        )

        provider_category = (
            MatchingEngine._normalize(
                provider_category
            )
        )

        if not requirement_category:
            return True

        if not provider_category:
            return False

        if requirement_category == provider_category:
            return True

        # Allow natural-language variations.
        aliases = {
            "laptop repair": {
                "laptop repair",
                "computer repair",
                "computer service",
                "electronics repair",
            },
            "electrical": {
                "electrical",
                "electrical repair",
                "electrician",
            },
            "home repair": {
                "home repair",
                "home maintenance",
                "handyman",
            },
            "cleaning": {
                "cleaning",
                "home cleaning",
                "house cleaning",
            },
            "packers and movers": {
                "packers and movers",
                "moving",
                "movers",
                "relocation",
            },
        }

        allowed_categories = aliases.get(
            requirement_category,
            {requirement_category},
        )

        return provider_category in allowed_categories

    @staticmethod
    def _category_score(
        requirement_category: str,
        provider_category: str,
        offer_category: str,
    ) -> float:

        if not requirement_category:
            return 70.0

        if MatchingEngine._category_matches(
            requirement_category,
            provider_category,
        ):
            return 100.0

        if MatchingEngine._category_matches(
            requirement_category,
            offer_category,
        ):
            return 100.0

        return 0.0

    # =========================================================
    # BUDGET
    # =========================================================

    @staticmethod
    def _budget_score(
        budget_min: float,
        budget_max: float,
        offer_price: float,
    ) -> float:

        if offer_price is None:
            return 50.0

        try:
            price = float(offer_price)
        except (TypeError, ValueError):
            return 0.0

        if price <= 0:
            return 0.0

        if budget_min is None and budget_max is None:
            return 70.0

        if budget_max is not None:

            if price <= budget_max:

                if budget_max == 0:
                    return 100.0

                difference = (
                    budget_max - price
                )

                percentage = (
                    difference / budget_max
                )

                return min(
                    100.0,
                    80.0 + percentage * 20.0,
                )

            over_budget = (
                price - budget_max
            ) / budget_max

            return max(
                0.0,
                80.0 - over_budget * 100.0,
            )

        if budget_min is not None:

            if price >= budget_min:
                return 100.0

            difference = (
                budget_min - price
            ) / budget_min

            return max(
                0.0,
                100.0 - difference * 100.0,
            )

        return 70.0

    # =========================================================
    # LOCATION
    # =========================================================

    @staticmethod
    def _location_score(
        requirement_location: str,
        provider_location: str,
    ) -> float:

        if not requirement_location:
            return 70.0

        if not provider_location:
            return 30.0

        requirement_location = (
            MatchingEngine._normalize(
                requirement_location
            )
        )

        provider_location = (
            MatchingEngine._normalize(
                provider_location
            )
        )

        if requirement_location in provider_location:
            return 100.0

        if provider_location in requirement_location:
            return 100.0

        return 20.0

    # =========================================================
    # AVAILABILITY
    # =========================================================

    @staticmethod
    def _availability_score(
        preferred_date: str,
        availability: str,
    ) -> float:

        if not preferred_date:
            return 70.0

        if not availability:
            return 40.0

        availability_text = (
            MatchingEngine._normalize(
                availability
            )
        )

        if (
            "available" in availability_text
            or "yes" in availability_text
            or "today" in availability_text
        ):
            return 100.0

        return 50.0

    # =========================================================
    # RATING
    # =========================================================

    @staticmethod
    def _rating_score(
        rating: float,
    ) -> float:

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return 0.0

        return min(
            100.0,
            max(
                0.0,
                (rating / 5.0) * 100.0,
            ),
        )

    # =========================================================
    # RECOMMENDATION REASON
    # =========================================================

    @staticmethod
    def _build_recommendation_reason(
        category_score: float,
        budget_score: float,
        location_score: float,
        availability_score: float,
        trust_score: float,
        rating_score: float,
        risk_score: float,
    ) -> str:

        reasons = []

        if category_score >= 90:
            reasons.append(
                "service category matches"
            )

        if budget_score >= 80:
            reasons.append(
                "budget fits well"
            )

        if location_score >= 80:
            reasons.append(
                "location matches"
            )

        if availability_score >= 80:
            reasons.append(
                "availability fits"
            )

        if trust_score >= 80:
            reasons.append(
                "strong provider trust"
            )

        if rating_score >= 80:
            reasons.append(
                "strong customer rating"
            )

        if risk_score < 25:
            reasons.append(
                "low risk"
            )
        elif risk_score >= 50:
            reasons.append(
                "elevated risk"
            )

        if not reasons:
            return (
                "Recommended based on the overall "
                "match across available factors."
            )

        return (
            "Recommended because "
            + ", ".join(reasons)
            + "."
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _normalize(value: Any) -> str:

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace("-", " ")
        )

    @staticmethod
    def _to_float(value: Any):

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None


matching_engine = MatchingEngine() 