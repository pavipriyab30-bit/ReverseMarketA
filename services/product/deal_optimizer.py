from typing import Any, Dict, Optional


class DealOptimizer:
    """
    BESTORA FIT Product Mode deal optimization engine.

    Evaluates whether a matched product represents a good deal
    for the user's requirements.
    """

    PRICE_WEIGHT = 40
    QUALITY_WEIGHT = 30
    BUDGET_WEIGHT = 20
    REVIEW_WEIGHT = 10

    def optimize(
        self,
        product: Dict[str, Any],
        budget_max: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate deal quality for a product.

        Returns the original product together with deal metrics.
        """

        if not isinstance(product, dict):
            raise ValueError("Product must be a dictionary.")

        price = product.get("price")

        if price is None:
            return {
                **product,
                "deal_score": 0.0,
                "deal_level": "UNKNOWN",
                "deal_reason": "Product price is unavailable.",
            }

        price = float(price)

        rating = float(
            product.get("rating") or 0
        )

        review_count = int(
            product.get("review_count") or 0
        )

        price_score = self._price_score(
            price,
            budget_max,
        )

        quality_score = self._quality_score(
            rating,
        )

        budget_score = self._budget_score(
            price,
            budget_max,
        )

        review_score = self._review_score(
            review_count,
        )

        deal_score = (
            price_score * self.PRICE_WEIGHT / 100
            + quality_score * self.QUALITY_WEIGHT / 100
            + budget_score * self.BUDGET_WEIGHT / 100
            + review_score * self.REVIEW_WEIGHT / 100
        )

        deal_score = round(
            min(100.0, max(0.0, deal_score)),
            2,
        )

        deal_level = self._deal_level(
            deal_score,
        )

        deal_reason = self._build_reason(
            price_score=price_score,
            quality_score=quality_score,
            budget_score=budget_score,
            review_score=review_score,
        )

        return {
            **product,
            "deal_score": deal_score,
            "deal_level": deal_level,
            "deal_reason": deal_reason,
        }

    @staticmethod
    def _price_score(
        price: float,
        budget_max: Optional[float],
    ) -> float:
        """
        Score the absolute price.

        When a budget is known, lower price within the budget
        receives a better score.
        """

        if price < 0:
            return 0.0

        if budget_max is None:
            return 70.0

        budget_max = float(budget_max)

        if budget_max <= 0:
            return 0.0

        if price > budget_max:
            return 0.0

        ratio = price / budget_max

        return min(
            100.0,
            max(
                0.0,
                100.0 - (ratio * 60.0),
            ),
        )

    @staticmethod
    def _quality_score(
        rating: float,
    ) -> float:
        """Convert a five-star rating into a 0–100 score."""

        if rating <= 0:
            return 0.0

        return min(
            100.0,
            (rating / 5.0) * 100.0,
        )

    @staticmethod
    def _budget_score(
        price: float,
        budget_max: Optional[float],
    ) -> float:
        """Score whether the product fits the user's budget."""

        if budget_max is None:
            return 70.0

        budget_max = float(budget_max)

        if budget_max <= 0:
            return 0.0

        if price > budget_max:
            return 0.0

        remaining_ratio = (
            budget_max - price
        ) / budget_max

        return min(
            100.0,
            70.0 + remaining_ratio * 30.0,
        )

    @staticmethod
    def _review_score(
        review_count: int,
    ) -> float:
        """Convert review volume into a confidence score."""

        if review_count <= 0:
            return 0.0

        return min(
            100.0,
            (review_count / 500.0) * 100.0,
        )

    @staticmethod
    def _deal_level(
        deal_score: float,
    ) -> str:
        """Convert a numeric deal score into a readable level."""

        if deal_score >= 85:
            return "EXCELLENT"

        if deal_score >= 70:
            return "GOOD"

        if deal_score >= 50:
            return "FAIR"

        if deal_score >= 30:
            return "WEAK"

        return "POOR"

    @staticmethod
    def _build_reason(
        price_score: float,
        quality_score: float,
        budget_score: float,
        review_score: float,
    ) -> str:
        reasons = []

        if price_score >= 80:
            reasons.append("competitive pricing")

        if quality_score >= 80:
            reasons.append("strong product rating")

        if budget_score >= 80:
            reasons.append("comfortable budget fit")

        if review_score >= 70:
            reasons.append("strong review volume")

        if not reasons:
            return "Deal quality is based on the available price and product data."

        return "Good deal because of " + ", ".join(reasons) + "."


# Shared Product Mode deal optimizer.
deal_optimizer = DealOptimizer() 