import unittest

from services.negotiation_engine import NegotiationEngine


class TestNegotiationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = NegotiationEngine()

    def test_original_price_is_preserved(self):
        strategy = self.engine.create_strategy(
            original_price=549,
            budget_max=550,
            trust_score=80,
            match_score=85
        )

        self.assertEqual(
            strategy["original_price"],
            549
        )

    def test_seller_price_moves_down(self):
        first = self.engine.simulate_seller_counter(
            original_price=549,
            buyer_offer=510,
            trust_score=80,
            match_score=85,
            previous_seller_price=549,
            negotiation_round=1
        )

        first_seller_price = first["seller_price"]

        second = self.engine.simulate_seller_counter(
            original_price=549,
            buyer_offer=515,
            trust_score=80,
            match_score=85,
            previous_seller_price=first_seller_price,
            negotiation_round=2
        )

        second_seller_price = second["seller_price"]

        self.assertLessEqual(
            second_seller_price,
            first_seller_price
        )

    def test_seller_never_increases_price(self):
        seller_price = 535

        result = self.engine.simulate_seller_counter(
            original_price=549,
            buyer_offer=515,
            trust_score=80,
            match_score=85,
            previous_seller_price=seller_price,
            negotiation_round=2
        )

        self.assertLessEqual(
            result["seller_price"],
            seller_price
        )

    def test_seller_never_goes_below_buyer_offer(self):
        result = self.engine.simulate_seller_counter(
            original_price=549,
            buyer_offer=520,
            trust_score=80,
            match_score=85,
            previous_seller_price=525,
            negotiation_round=4
        )

        self.assertGreaterEqual(
            result["seller_price"],
            520
        )

    def test_accept_when_buyer_matches_seller(self):
        result = self.engine.simulate_seller_counter(
            original_price=549,
            buyer_offer=525,
            trust_score=80,
            match_score=85,
            previous_seller_price=525,
            negotiation_round=4
        )

        self.assertEqual(
            result["status"],
            "ACCEPT"
        )

        self.assertEqual(
            result["seller_price"],
            525
        )

    def test_final_deal_cannot_exceed_original_price(self):
        result = self.engine.finalize_deal(
            original_price=549,
            final_price=550
        )

        self.assertFalse(
            result["success"]
        )

    def test_realistic_discount_limit(self):
        result = self.engine.finalize_deal(
            original_price=549,
            final_price=400
        )

        self.assertFalse(
            result["success"]
        )


if __name__ == "__main__":
    unittest.main() 