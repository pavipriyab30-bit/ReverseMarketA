"""
BESTORA FIT
Negotiation Engine

Responsibilities:
- Create AI negotiation strategy
- Calculate opening / target / walk-away prices
- Simulate controlled seller counters
- Preserve seller price progression
- Never increase seller price
- Automatically accept when buyer and seller are within ₹10
- Finalize deals
- Generate negotiation messages
"""

from typing import Any, Dict, Optional


class NegotiationEngine:
    """Controlled negotiation engine for BESTORA FIT."""

    # =========================================================
    # PRICE HELPERS
    # =========================================================

    @staticmethod
    def _validate_price(
        value: float,
        field_name: str
    ) -> float:

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field_name} must be a valid number."
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return value

    @staticmethod
    def _round_negotiation_price(
        value: float
    ) -> int:
        """
        Round negotiation prices to realistic values.

        Under ₹1,000:
            nearest ₹5

        ₹1,000 - ₹9,999:
            nearest ₹10

        ₹10,000+:
            nearest ₹50
        """

        value = float(value)

        if value < 1000:
            step = 5
        elif value < 10000:
            step = 10
        else:
            step = 50

        return int(
            round(value / step) * step
        )

    # =========================================================
    # NEGOTIATION STRATEGY
    # =========================================================

    def create_strategy(
        self,
        original_price: float,
        budget_max: Optional[float] = None,
        trust_score: float = 50,
        match_score: float = 50,
    ) -> Dict[str, Any]:

        original_price = self._validate_price(
            original_price,
            "original_price"
        )

        if budget_max is not None:
            budget_max = self._validate_price(
                budget_max,
                "budget_max"
            )

        trust_score = min(
            max(float(trust_score), 0.0),
            100.0
        )

        match_score = min(
            max(float(match_score), 0.0),
            100.0
        )

        # -----------------------------------------------------
        # QUALITY
        # -----------------------------------------------------

        quality_score = (
            trust_score * 0.55 +
            match_score * 0.45
        )

        quality_factor = (
            quality_score / 100.0
        )

        # -----------------------------------------------------
        # OPENING PRICE
        # -----------------------------------------------------

        opening_discount = (
            0.08 +
            ((1.0 - quality_factor) * 0.10)
        )

        opening_price = (
            original_price *
            (1.0 - opening_discount)
        )

        # -----------------------------------------------------
        # TARGET PRICE
        # -----------------------------------------------------

        target_discount = (
            0.05 +
            ((1.0 - quality_factor) * 0.07)
        )

        target_price = (
            original_price *
            (1.0 - target_discount)
        )

        # -----------------------------------------------------
        # WALK-AWAY PRICE
        # -----------------------------------------------------

        walk_away_price = (
            original_price * 0.85
        )

        # -----------------------------------------------------
        # BUDGET LIMIT
        # -----------------------------------------------------

        if budget_max is not None:

            target_price = min(
                target_price,
                budget_max
            )

            walk_away_price = min(
                walk_away_price,
                budget_max
            )

        # -----------------------------------------------------
        # ROUND
        # -----------------------------------------------------

        opening_price = (
            self._round_negotiation_price(
                opening_price
            )
        )

        target_price = (
            self._round_negotiation_price(
                target_price
            )
        )

        walk_away_price = (
            self._round_negotiation_price(
                walk_away_price
            )
        )

        # Never exceed original price.

        opening_price = min(
            opening_price,
            original_price
        )

        target_price = min(
            target_price,
            original_price
        )

        walk_away_price = min(
            walk_away_price,
            original_price
        )

        # Keep prices logically ordered.

        target_price = min(
            target_price,
            opening_price
        )

        walk_away_price = min(
            walk_away_price,
            target_price
        )

        # -----------------------------------------------------
        # SAVINGS
        # -----------------------------------------------------

        potential_saving = max(
            original_price -
            target_price,
            0
        )

        maximum_saving = max(
            original_price -
            walk_away_price,
            0
        )

        if original_price > 0:

            potential_saving_percentage = (
                potential_saving /
                original_price
            ) * 100

        else:

            potential_saving_percentage = 0

        # -----------------------------------------------------
        # CONFIDENCE
        # -----------------------------------------------------

        confidence = (
            trust_score * 0.45 +
            match_score * 0.35 +
            20.0
        )

        confidence = min(
            max(confidence, 0.0),
            100.0
        )

        if confidence >= 80:
            confidence_level = "HIGH"

        elif confidence >= 60:
            confidence_level = "MEDIUM"

        else:
            confidence_level = "LOW"

        # -----------------------------------------------------
        # EXPLANATION
        # -----------------------------------------------------

        if quality_score >= 80:

            reason = (
                "The provider has strong trust and match "
                "signals, so the AI recommends a controlled "
                "opening offer."
            )

        elif quality_score >= 60:

            reason = (
                "The AI balances provider trust, service fit "
                "and potential savings to create a realistic "
                "negotiation range."
            )

        else:

            reason = (
                "The AI uses a conservative negotiation range "
                "because trust or service-fit signals are weaker."
            )

        return {
            "original_price": original_price,
            "budget_max": budget_max,

            "opening_price": opening_price,
            "target_price": target_price,
            "walk_away_price": walk_away_price,

            "potential_saving": potential_saving,
            "maximum_saving": maximum_saving,

            "potential_saving_percentage": round(
                potential_saving_percentage,
                1
            ),

            "trust_score": round(
                trust_score,
                1
            ),

            "match_score": round(
                match_score,
                1
            ),

            "confidence": round(
                confidence,
                1
            ),

            "confidence_level": confidence_level,

            "reason": reason,
        }

    # =========================================================
    # SELLER COUNTER
    # =========================================================

    def simulate_seller_counter(
        self,
        original_price: float,
        buyer_offer: float,
        trust_score: float = 50,
        match_score: float = 50,
        previous_seller_price: Optional[float] = None,
        negotiation_round: int = 1,
    ) -> Dict[str, Any]:

        original_price = self._validate_price(
            original_price,
            "original_price"
        )

        buyer_offer = self._validate_price(
            buyer_offer,
            "buyer_offer"
        )

        trust_score = min(
            max(float(trust_score), 0.0),
            100.0
        )

        match_score = min(
            max(float(match_score), 0.0),
            100.0
        )

        try:
            negotiation_round = int(
                negotiation_round
            )
        except (TypeError, ValueError):
            negotiation_round = 1

        negotiation_round = max(
            negotiation_round,
            1
        )

        # -----------------------------------------------------
        # BUYER CANNOT EXCEED LISTED PRICE
        # -----------------------------------------------------

        if buyer_offer > original_price:

            raise ValueError(
                "Buyer offer cannot exceed original price."
            )

        # -----------------------------------------------------
        # ESTABLISH CURRENT SELLER PRICE
        # -----------------------------------------------------

        if previous_seller_price is None:

            previous_seller_price = (
                original_price
            )

        else:

            previous_seller_price = (
                self._validate_price(
                    previous_seller_price,
                    "previous_seller_price"
                )
            )

        # Seller can never be above listed price.

        previous_seller_price = min(
            previous_seller_price,
            original_price
        )

        # Seller cannot be below the buyer's
        # current offer.

        previous_seller_price = max(
            previous_seller_price,
            buyer_offer
        )

        # =====================================================
        # RULE 1
        # BUYER ALREADY MATCHES SELLER
        # =====================================================

        current_gap = (
            previous_seller_price -
            buyer_offer
        )

        if current_gap <= 0:

            return {
                "status": "ACCEPT",
                "seller_price": round(
                    buyer_offer,
                    2
                ),
                "previous_seller_price":
                    previous_seller_price,
                "buyer_offer":
                    buyer_offer,
                "gap": 0,
                "negotiation_round":
                    negotiation_round,
                "accepted": True,
                "message": (
                    f"The seller accepted your offer "
                    f"of ₹{buyer_offer:,.0f}."
                ),
            }

        # =====================================================
        # RULE 2
        # WITHIN ₹10 = DEAL
        # =====================================================

        if current_gap <= 10:

            final_price = max(
                buyer_offer,
                previous_seller_price
            )

            final_price = min(
                final_price,
                original_price
            )

            return {
                "status": "ACCEPT",
                "seller_price": round(
                    final_price,
                    2
                ),
                "previous_seller_price":
                    previous_seller_price,
                "buyer_offer":
                    buyer_offer,
                "gap":
                    current_gap,
                "negotiation_round":
                    negotiation_round,
                "accepted": True,
                "message": (
                    f"The seller accepted at "
                    f"₹{final_price:,.0f}. "
                    f"The remaining difference was "
                    f"only ₹{current_gap:,.0f}."
                ),
            }

        # =====================================================
        # SELLER COOPERATION
        # =====================================================

        cooperation = (
            trust_score * 0.60 +
            match_score * 0.40
        ) / 100.0

        # Higher cooperation = stronger concession.

        base_concession_rate = (
            0.25 +
            (cooperation * 0.12)
        )

        # Later rounds create slightly larger concessions.

        round_bonus = min(
            (negotiation_round - 1) * 0.04,
            0.16
        )

        concession_rate = (
            base_concession_rate +
            round_bonus
        )

        concession_rate = min(
            max(
                concession_rate,
                0.25
            ),
            0.48
        )

        # =====================================================
        # CALCULATE SELLER MOVEMENT
        # =====================================================

        gap = (
            previous_seller_price -
            buyer_offer
        )

        concession = (
            gap *
            concession_rate
        )

        proposed_seller_price = (
            previous_seller_price -
            concession
        )

        seller_price = (
            self._round_negotiation_price(
                proposed_seller_price
            )
        )

        # =====================================================
        # CRITICAL SAFETY RULE
        #
        # SELLER PRICE MUST ALWAYS MOVE DOWN.
        # =====================================================

        if seller_price >= previous_seller_price:

            seller_price = (
                self._round_negotiation_price(
                    previous_seller_price - 5
                )
            )

        # Absolute protection.

        seller_price = min(
            seller_price,
            previous_seller_price - 5
        )

        # Seller cannot go below buyer offer.

        seller_price = max(
            seller_price,
            buyer_offer
        )

        # Seller cannot exceed original price.

        seller_price = min(
            seller_price,
            original_price
        )

        # =====================================================
        # FINAL SAFETY NORMALIZATION
        # =====================================================

        if seller_price > previous_seller_price:

            seller_price = (
                previous_seller_price
            )

        # =====================================================
        # NEW GAP
        # =====================================================

        remaining_gap = (
            seller_price -
            buyer_offer
        )

        remaining_gap = max(
            remaining_gap,
            0
        )

        # =====================================================
        # RULE 3
        # AUTOMATIC ACCEPTANCE WITHIN ₹10
        # =====================================================

        if remaining_gap <= 10:

            final_price = max(
                seller_price,
                buyer_offer
            )

            final_price = min(
                final_price,
                original_price
            )

            return {
                "status": "ACCEPT",
                "seller_price": round(
                    final_price,
                    2
                ),
                "previous_seller_price":
                    previous_seller_price,
                "buyer_offer":
                    buyer_offer,
                "gap":
                    remaining_gap,
                "negotiation_round":
                    negotiation_round,
                "accepted": True,
                "message": (
                    f"The seller moved to "
                    f"₹{final_price:,.0f}. "
                    f"The remaining gap is only "
                    f"₹{remaining_gap:,.0f}, so the "
                    f"deal is ready to finalize."
                ),
            }

        # =====================================================
        # RULE 4
        # NEAR AGREEMENT
        # =====================================================

        if remaining_gap <= 30:

            return {
                "status":
                    "NEAR_AGREEMENT",

                "seller_price":
                    round(
                        seller_price,
                        2
                    ),

                "previous_seller_price":
                    previous_seller_price,

                "buyer_offer":
                    buyer_offer,

                "gap":
                    remaining_gap,

                "negotiation_round":
                    negotiation_round,

                "accepted":
                    False,

                "message": (
                    f"The seller moved to "
                    f"₹{seller_price:,.0f}. "
                    f"You're very close to agreement."
                ),
            }

        # =====================================================
        # RULE 5
        # SELLER FIRM AFTER MANY ROUNDS
        # =====================================================

        if (
            negotiation_round >= 5 and
            remaining_gap > 15
        ):

            return {
                "status":
                    "SELLER_FIRM",

                "seller_price":
                    round(
                        seller_price,
                        2
                    ),

                "previous_seller_price":
                    previous_seller_price,

                "buyer_offer":
                    buyer_offer,

                "gap":
                    remaining_gap,

                "negotiation_round":
                    negotiation_round,

                "accepted":
                    False,

                "message": (
                    f"The seller is holding firm at "
                    f"₹{seller_price:,.0f}."
                ),
            }

        # =====================================================
        # NORMAL COUNTER
        # =====================================================

        return {
            "status":
                "COUNTER",

            "seller_price":
                round(
                    seller_price,
                    2
                ),

            "previous_seller_price":
                previous_seller_price,

            "buyer_offer":
                buyer_offer,

            "gap":
                remaining_gap,

            "negotiation_round":
                negotiation_round,

            "accepted":
                False,

            "message": (
                f"The seller countered at "
                f"₹{seller_price:,.0f}."
            ),
        }

    # =========================================================
    # EVALUATE COUNTER
    # =========================================================

    def evaluate_counter(
        self,
        original_price: float,
        buyer_offer: float,
        seller_price: float,
        budget_max: Optional[float] = None,
    ) -> Dict[str, Any]:

        original_price = self._validate_price(
            original_price,
            "original_price"
        )

        buyer_offer = self._validate_price(
            buyer_offer,
            "buyer_offer"
        )

        seller_price = self._validate_price(
            seller_price,
            "seller_price"
        )

        gap = max(
            seller_price -
            buyer_offer,
            0
        )

        if gap <= 10:

            recommendation = "ACCEPT"

        elif gap <= 30:

            recommendation = "CONSIDER"

        else:

            recommendation = "NEGOTIATE"

        budget_warning = False

        if budget_max is not None:

            budget_max = self._validate_price(
                budget_max,
                "budget_max"
            )

            budget_warning = (
                seller_price >
                budget_max
            )

        return {
            "original_price":
                original_price,

            "buyer_offer":
                buyer_offer,

            "seller_price":
                seller_price,

            "gap":
                gap,

            "recommendation":
                recommendation,

            "budget_warning":
                budget_warning,
        }

    # =========================================================
    # FINALIZE DEAL
    # =========================================================

    def finalize_deal(
        self,
        original_price: float,
        final_price: float,
        budget_max: Optional[float] = None,
    ) -> Dict[str, Any]:

        original_price = self._validate_price(
            original_price,
            "original_price"
        )

        final_price = self._validate_price(
            final_price,
            "final_price"
        )

        if final_price > original_price:

            raise ValueError(
                "Final price cannot exceed original price."
            )

        savings = max(
            original_price -
            final_price,
            0
        )

        savings_percentage = (
            savings /
            original_price
        ) * 100

        # Controlled maximum discount.

        if savings_percentage > 15:

            raise ValueError(
                "Negotiated discount exceeds the "
                "allowed 15% limit."
            )

        budget_warning = False

        if budget_max is not None:

            budget_max = self._validate_price(
                budget_max,
                "budget_max"
            )

            budget_warning = (
                final_price >
                budget_max
            )

        return {
            "success": True,

            "original_price":
                original_price,

            "final_price":
                final_price,

            "savings":
                savings,

            "savings_percentage":
                round(
                    savings_percentage,
                    1
                ),

            "budget_warning":
                budget_warning,

            "message":
                (
                    f"Deal successfully accepted at "
                    f"₹{final_price:,.0f}."
                ),
        }

    # =========================================================
    # NEGOTIATION MESSAGE
    # =========================================================

    def generate_message(
        self,
        provider_name: str,
        offer_title: str,
        original_price: float,
        proposed_price: float,
        user_requirement: str = "",
    ) -> str:

        original_price = self._validate_price(
            original_price,
            "original_price"
        )

        proposed_price = self._validate_price(
            proposed_price,
            "proposed_price"
        )

        if proposed_price > original_price:

            proposed_price = original_price

        savings = max(
            original_price -
            proposed_price,
            0
        )

        if savings > 0:

            savings_text = (
                f"This would save "
                f"₹{savings:,.0f}."
            )

        else:

            savings_text = ""

        requirement_text = ""

        if user_requirement:

            requirement_text = (
                " I am looking for a service that "
                "matches my stated requirements."
            )

        return (
            f"Hi {provider_name}, "
            f"I am interested in your "
            f"{offer_title} service. "
            f"Your listed price is "
            f"₹{original_price:,.0f}, and I would "
            f"like to offer ₹{proposed_price:,.0f}. "
            f"{savings_text}"
            f"{requirement_text} "
            f"If this works for you, I would be "
            f"happy to proceed with the booking."
        )


# =============================================================
# GLOBAL INSTANCE
# =============================================================

negotiation_engine = NegotiationEngine() 