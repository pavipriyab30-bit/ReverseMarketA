from typing import Any, Dict, List, Optional

from services.product.product_search import product_search


class ProductMatcher:
    """
    BESTORA FIT Product Mode matching engine.

    Converts product-search results into ranked recommendations
    using requirement-based scoring.
    """

    CATEGORY_WEIGHT = 30
    BUDGET_WEIGHT = 20
    FEATURE_WEIGHT = 20
    QUALITY_WEIGHT = 15
    VALUE_WEIGHT = 15

    def find_matches(
        self,
        requirement: Dict[str, Any],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find and rank products for a structured requirement.
        """

        if not isinstance(requirement, dict):
            raise ValueError("Requirement must be a dictionary.")

        if limit <= 0:
            raise ValueError("Match limit must be greater than zero.")

        products = product_search.search(
            query=requirement.get("query", ""),
            category=requirement.get("category"),
            budget_min=requirement.get("budget_min"),
            budget_max=requirement.get("budget_max"),
            preferred_brands=requirement.get(
                "preferred_brands",
                [],
            ),
            required_features=requirement.get(
                "required_features",
                [],
            ),
            limit=max(limit * 2, 20),
        )

        matches = []

        for product in products:
            category_score = self._category_score(
                product,
                requirement,
            )

            budget_score = self._budget_score(
                product,
                requirement,
            )

            feature_score = self._feature_score(
                product,
                requirement,
            )

            quality_score = self._quality_score(
                product,
            )

            value_score = self._value_score(
                product,
                requirement,
            )

            match_score = (
                category_score * self.CATEGORY_WEIGHT / 100
                + budget_score * self.BUDGET_WEIGHT / 100
                + feature_score * self.FEATURE_WEIGHT / 100
                + quality_score * self.QUALITY_WEIGHT / 100
                + value_score * self.VALUE_WEIGHT / 100
            )

            recommendation_reason = self._build_reason(
                product=product,
                category_score=category_score,
                budget_score=budget_score,
                feature_score=feature_score,
                quality_score=quality_score,
                value_score=value_score,
            )

            matches.append(
                {
                    "product": product,
                    "match_score": round(match_score, 2),
                    "category_score": round(category_score, 2),
                    "budget_score": round(budget_score, 2),
                    "feature_score": round(feature_score, 2),
                    "quality_score": round(quality_score, 2),
                    "value_score": round(value_score, 2),
                    "recommendation_reason": recommendation_reason,
                }
            )

        matches.sort(
            key=lambda item: item["match_score"],
            reverse=True,
        )

        return matches[:limit]

    @staticmethod
    def _category_score(
        product: Dict[str, Any],
        requirement: Dict[str, Any],
    ) -> float:
        category = str(
            requirement.get("category") or ""
        ).strip().lower()

        if not category:
            return 100.0

        product_category = str(
            product.get("category") or ""
        ).strip().lower()

        if not product_category:
            return 0.0

        if category == product_category:
            return 100.0

        if category in product_category:
            return 90.0

        if product_category in category:
            return 85.0

        return 0.0

    @staticmethod
    def _budget_score(
        product: Dict[str, Any],
        requirement: Dict[str, Any],
    ) -> float:
        price = product.get("price")

        if price is None:
            return 0.0

        price = float(price)

        budget_min = requirement.get("budget_min")
        budget_max = requirement.get("budget_max")

        if budget_min is None and budget_max is None:
            return 70.0

        if budget_max is not None:
            budget_max = float(budget_max)

            if price > budget_max:
                return 0.0

            if price == budget_max:
                return 80.0

            if budget_max > 0:
                savings_ratio = (
                    budget_max - price
                ) / budget_max

                return min(
                    100.0,
                    80.0 + savings_ratio * 20.0,
                )

        if budget_min is not None:
            budget_min = float(budget_min)

            if price < budget_min:
                return 70.0

        return 80.0

    @staticmethod
    def _feature_score(
        product: Dict[str, Any],
        requirement: Dict[str, Any],
    ) -> float:
        required_features = requirement.get(
            "required_features",
            [],
        )

        if not required_features:
            return 70.0

        searchable_text = " ".join(
            [
                str(product.get("name") or ""),
                str(product.get("brand") or ""),
                str(product.get("category") or ""),
                str(product.get("description") or ""),
            ]
        ).lower()

        matched = 0

        for feature in required_features:
            feature = str(feature).strip().lower()

            if feature and feature in searchable_text:
                matched += 1

        if not required_features:
            return 70.0

        return (
            matched / len(required_features)
        ) * 100.0

    @staticmethod
    def _quality_score(
        product: Dict[str, Any],
    ) -> float:
        rating = float(
            product.get("rating") or 0
        )

        review_count = int(
            product.get("review_count") or 0
        )

        rating_score = min(
            100.0,
            (rating / 5.0) * 100.0,
        )

        review_score = min(
            100.0,
            review_count / 500.0 * 100.0,
        )

        return (
            rating_score * 0.7
            + review_score * 0.3
        )

    @staticmethod
    def _value_score(
        product: Dict[str, Any],
        requirement: Dict[str, Any],
    ) -> float:
        price = product.get("price")

        if price is None:
            return 0.0

        rating = float(
            product.get("rating") or 0
        )

        budget_max = requirement.get("budget_max")

        quality_factor = min(
            1.0,
            rating / 5.0,
        )

        if budget_max is not None:
            budget_max = float(budget_max)

            if budget_max <= 0:
                return 0.0

            if price > budget_max:
                return 0.0

            price_factor = (
                budget_max - price
            ) / budget_max

            return min(
                100.0,
                (
                    quality_factor * 70
                    + price_factor * 30
                ),
            )

        return min(
            100.0,
            quality_factor * 100,
        )

    @staticmethod
    def _build_reason(
        product: Dict[str, Any],
        category_score: float,
        budget_score: float,
        feature_score: float,
        quality_score: float,
        value_score: float,
    ) -> str:
        reasons = []

        if category_score >= 85:
            reasons.append("strong category match")

        if budget_score >= 80:
            reasons.append("fits your budget")

        if feature_score >= 80:
            reasons.append("matches required features")

        if quality_score >= 80:
            reasons.append("strong ratings and reviews")

        if value_score >= 80:
            reasons.append("good overall value")

        if not reasons:
            reasons.append("best available match based on your requirements")

        return "Recommended because it has " + ", ".join(reasons) + "."


# Shared Product Mode matcher.
product_matcher = ProductMatcher() 