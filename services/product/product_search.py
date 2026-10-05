from typing import Any, Dict, List, Optional

from database.database import get_database
from models.product import Product


class ProductSearch:
    """
    Product discovery engine for BESTORA FIT Product Mode.

    Search is intentionally broad enough to provide candidates
    to the Product Matcher. Requirement-specific scoring belongs
    to product_matcher.py.
    """

    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        preferred_brands: Optional[List[str]] = None,
        required_features: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search the product catalogue for suitable candidates."""

        if limit <= 0:
            raise ValueError(
                "Search limit must be greater than zero."
            )

        query = (query or "").strip()
        category = (category or "").strip()

        preferred_brands = [
            brand.strip().lower()
            for brand in (preferred_brands or [])
            if isinstance(brand, str) and brand.strip()
        ]

        connection = get_database()

        try:
            rows = connection.execute(
                """
                SELECT *
                FROM products
                WHERE availability = 'available'
                ORDER BY
                    rating DESC,
                    review_count DESC,
                    price ASC
                LIMIT ?
                """,
                (max(limit * 5, limit),),
            ).fetchall()

            products = []

            for row in rows:
                product = Product.from_row(row)

                if not self._matches_category(
                    product,
                    category,
                ):
                    continue

                if not self._matches_budget(
                    product,
                    budget_min,
                    budget_max,
                ):
                    continue

                if not self._matches_query(
                    product,
                    query,
                ):
                    continue

                if not self._matches_brand(
                    product,
                    preferred_brands,
                ):
                    continue

                products.append(
                    product.to_dict()
                )

                if len(products) >= limit:
                    break

            return products

        finally:
            connection.close()

    def get_by_id(
        self,
        product_id: int,
    ) -> Optional[Dict[str, Any]]:
        """Return a product by database ID."""

        connection = get_database()

        try:
            row = connection.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                """,
                (product_id,),
            ).fetchone()

            if row is None:
                return None

            return Product.from_row(row).to_dict()

        finally:
            connection.close()

    @staticmethod
    def _matches_category(
        product: Product,
        category: str,
    ) -> bool:
        """Check whether the product belongs to the requested category."""

        if not category:
            return True

        product_category = (
            product.category or ""
        ).strip().lower()

        requested_category = (
            category.strip().lower()
        )

        return (
            requested_category in product_category
            or product_category in requested_category
        )

    @staticmethod
    def _matches_budget(
        product: Product,
        budget_min: Optional[float],
        budget_max: Optional[float],
    ) -> bool:
        """Check whether the product fits the requested budget."""

        if product.price is None:
            return False

        price = float(product.price)

        if budget_min is not None:
            if price < float(budget_min):
                return False

        if budget_max is not None:
            if price > float(budget_max):
                return False

        return True

    @staticmethod
    def _matches_query(
        product: Product,
        query: str,
    ) -> bool:
        """
        Check broad textual relevance.

        Feature-level matching is intentionally handled by the
        matcher rather than being used as a hard search filter.
        """

        if not query:
            return True

        searchable_text = " ".join(
            [
                product.name or "",
                product.brand or "",
                product.category or "",
                product.description or "",
            ]
        ).lower()

        query_words = [
            word.strip().lower()
            for word in query.split()
            if word.strip()
        ]

        if not query_words:
            return True

        # Category/product terms are enough to retrieve candidates.
        # Do not require every natural-language feature to appear
        # literally in the catalogue description.
        meaningful_words = [
            word
            for word in query_words
            if len(word) >= 3
        ]

        if not meaningful_words:
            return True

        return any(
            word in searchable_text
            for word in meaningful_words
        )

    @staticmethod
    def _matches_brand(
        product: Product,
        preferred_brands: List[str],
    ) -> bool:
        """Check preferred brand requirements."""

        if not preferred_brands:
            return True

        product_brand = (
            product.brand or ""
        ).strip().lower()

        return any(
            brand in product_brand
            or product_brand in brand
            for brand in preferred_brands
        )


# Shared Product Mode search service.
product_search = ProductSearch() 