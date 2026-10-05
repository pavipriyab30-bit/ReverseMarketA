import unittest


from services.product.product_requirement_parser import (
    product_requirement_parser,
)
from services.product.product_search import product_search
from services.product.product_matcher import product_matcher
from services.product.deal_optimizer import deal_optimizer


class ProductModeTests(unittest.TestCase):

    def test_requirement_parser(self):
        requirement = product_requirement_parser.parse(
            "I need a laptop under ₹50000 with 16GB RAM"
        )

        self.assertIsInstance(
            requirement,
            dict,
        )

        self.assertIn(
            "category",
            requirement,
        )

        self.assertIn(
            "budget_max",
            requirement,
        )

        self.assertIn(
            "required_features",
            requirement,
        )

    def test_product_search(self):
        products = product_search.search(
            category="Laptop",
            budget_max=50000,
            limit=5,
        )

        self.assertIsInstance(
            products,
            list,
        )

        for product in products:
            self.assertEqual(
                product["category"],
                "Laptop",
            )

            self.assertLessEqual(
                product["price"],
                50000,
            )

    def test_product_matcher(self):
        requirement = {
            "query": "laptop",
            "category": "Laptop",
            "budget_min": None,
            "budget_max": 50000,
            "preferred_brands": [],
            "required_features": [],
            "preferred_features": [],
            "excluded_features": [],
        }

        matches = product_matcher.find_matches(
            requirement,
            limit=5,
        )

        self.assertIsInstance(
            matches,
            list,
        )

        if matches:
            self.assertIn(
                "product",
                matches[0],
            )

            self.assertIn(
                "match_score",
                matches[0],
            )

            self.assertIn(
                "recommendation_reason",
                matches[0],
            )

    def test_deal_optimizer(self):
        product = {
            "name": "Test Laptop",
            "price": 40000,
            "rating": 4.6,
            "review_count": 500,
        }

        result = deal_optimizer.optimize(
            product,
            budget_max=50000,
        )

        self.assertIn(
            "deal_score",
            result,
        )

        self.assertIn(
            "deal_level",
            result,
        )

        self.assertIn(
            "deal_reason",
            result,
        )

        self.assertGreaterEqual(
            result["deal_score"],
            0,
        )

        self.assertLessEqual(
            result["deal_score"],
            100,
        )


if __name__ == "__main__":
    unittest.main() 