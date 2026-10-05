"""
BESTORA FIT
Negotiation Routes

Handles:
- Negotiation page
- Strategy
- Progressive seller counters
- Counter evaluation
- Deal finalization
- Negotiation message generation
"""

from flask import Blueprint, jsonify, render_template, request

from services.negotiation_engine import negotiation_engine


negotiation_bp = Blueprint(
    "negotiation",
    __name__,
    url_prefix="/negotiation"
)


# =========================================================
# HELPERS
# =========================================================

def get_json_body():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        raise ValueError(
            "Request body must be valid JSON."
        )

    return data


def require_number(data, key):
    value = data.get(key)

    if value is None:
        raise ValueError(
            f"Missing required field: {key}"
        )

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{key} must be a valid number."
        )

    return number


def optional_number(data, key, default=None):
    value = data.get(key)

    if value is None or value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{key} must be a valid number."
        )


def optional_integer(data, key, default=1):
    value = data.get(key)

    if value is None or value == "":
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{key} must be a valid integer."
        )


def error_response(message, status=400):
    return jsonify({
        "success": False,
        "error": message
    }), status


# =========================================================
# NEGOTIATION PAGE
# =========================================================

@negotiation_bp.route("/", methods=["GET"])
def negotiation_page():

    return render_template(
        "negotiation/negotiation.html"
    )


# =========================================================
# CREATE STRATEGY
# =========================================================

@negotiation_bp.route(
    "/strategy",
    methods=["POST"]
)
def create_strategy():

    try:

        data = get_json_body()

        original_price = require_number(
            data,
            "original_price"
        )

        budget_max = optional_number(
            data,
            "budget_max"
        )

        trust_score = optional_number(
            data,
            "trust_score",
            50
        )

        match_score = optional_number(
            data,
            "match_score",
            50
        )


        strategy = (
            negotiation_engine.create_strategy(
                original_price=original_price,
                budget_max=budget_max,
                trust_score=trust_score,
                match_score=match_score
            )
        )


        

        strategy["trust_score"] = trust_score
        strategy["match_score"] = match_score


        return jsonify({
            "success": True,
            "strategy": strategy
        })


    except ValueError as error:

        return error_response(
            str(error)
        )


    except Exception as error:

        return error_response(
            f"Unable to create negotiation strategy: {error}",
            500
        )


# =========================================================
# SELLER COUNTER
# =========================================================

@negotiation_bp.route(
    "/seller-counter",
    methods=["POST"]
)
def seller_counter():

    try:

        data = get_json_body()


        # -------------------------------------------------
        # REQUIRED VALUES
        # -------------------------------------------------

        original_price = require_number(
            data,
            "original_price"
        )

        buyer_offer = require_number(
            data,
            "buyer_offer"
        )


        # -------------------------------------------------
        # OPTIONAL VALUES
        # -------------------------------------------------

        trust_score = optional_number(
            data,
            "trust_score",
            50
        )

        match_score = optional_number(
            data,
            "match_score",
            50
        )

        negotiation_round = optional_integer(
            data,
            "negotiation_round",
            1
        )


        # -------------------------------------------------
        # CRITICAL STATE
        #
        # This MUST come from the frontend after the
        # first seller response.
        #
        # Example:
        #
        # Round 1:
        # original = 549
        # seller   = 535
        #
        # Round 2:
        # previous_seller_price MUST be 535
        #
        # NOT 549.
        # -------------------------------------------------

        previous_seller_price = optional_number(
            data,
            "previous_seller_price"
        )


        # -------------------------------------------------
        # FIRST ROUND
        #
        # If no previous seller price exists, the selected
        # database offer is the starting seller price.
        # -------------------------------------------------

        if previous_seller_price is None:

            previous_seller_price = (
                original_price
            )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if original_price <= 0:

            raise ValueError(
                "Original price must be greater than zero."
            )


        if buyer_offer <= 0:

            raise ValueError(
                "Buyer offer must be greater than zero."
            )


        if buyer_offer > original_price:

            raise ValueError(
                "Buyer offer cannot exceed original price."
            )


        if previous_seller_price <= 0:

            raise ValueError(
                "Previous seller price must be greater than zero."
            )


        if previous_seller_price > original_price:

            previous_seller_price = (
                original_price
            )


        # -------------------------------------------------
        # IMPORTANT SAFETY RULE
        #
        # Seller price can NEVER be lower than buyer offer
        # before the engine evaluates acceptance.
        # -------------------------------------------------

        previous_seller_price = max(
            buyer_offer,
            previous_seller_price
        )


        # -------------------------------------------------
        # CALL NEGOTIATION ENGINE
        # -------------------------------------------------

        result = (
            negotiation_engine.simulate_seller_counter(
                original_price=original_price,
                buyer_offer=buyer_offer,
                trust_score=trust_score,
                match_score=match_score,
                previous_seller_price=previous_seller_price,
                negotiation_round=negotiation_round
            )
        )


        # -------------------------------------------------
        # FINAL SERVER-SIDE SAFETY CHECK
        #
        # A seller is NEVER allowed to increase price.
        #
        # Example:
        #
        # previous = 530
        # returned = 535
        #
        # This is invalid.
        #
        # Instead of allowing it to reach the browser,
        # force the next seller price down.
        # -------------------------------------------------

        seller_price = float(
            result.get(
                "seller_price",
                previous_seller_price
            )
        )


        if seller_price > previous_seller_price:

            seller_price = (
                previous_seller_price - 5
            )


        # Seller can never go below buyer offer.
        seller_price = max(
            buyer_offer,
            seller_price
        )


        # Never exceed original price.
        seller_price = min(
            original_price,
            seller_price
        )


        result["seller_price"] = round(
            seller_price,
            2
        )


        # -------------------------------------------------
        # RETURN COMPLETE STATE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "result": result,

            "state": {

                "original_price":
                    round(
                        original_price,
                        2
                    ),

                "buyer_offer":
                    round(
                        buyer_offer,
                        2
                    ),

                "previous_seller_price":
                    round(
                        previous_seller_price,
                        2
                    ),

                "seller_price":
                    round(
                        seller_price,
                        2
                    ),

                "negotiation_round":
                    negotiation_round
            }
        })


    except ValueError as error:

        return error_response(
            str(error)
        )


    except Exception as error:

        return error_response(
            f"Unable to process seller counter: {error}",
            500
        )


# =========================================================
# EVALUATE COUNTER
# =========================================================

@negotiation_bp.route(
    "/evaluate-counter",
    methods=["POST"]
)
def evaluate_counter():

    try:

        data = get_json_body()


        original_price = require_number(
            data,
            "original_price"
        )

        buyer_offer = require_number(
            data,
            "buyer_offer"
        )

        seller_price = require_number(
            data,
            "seller_price"
        )

        walk_away_price = optional_number(
            data,
            "walk_away_price"
        )


        result = (
            negotiation_engine.evaluate_counter(
                original_price=original_price,
                buyer_offer=buyer_offer,
                seller_price=seller_price,
                walk_away_price=walk_away_price
            )
        )


        return jsonify({
            "success": True,
            "result": result
        })


    except ValueError as error:

        return error_response(
            str(error)
        )


    except Exception as error:

        return error_response(
            f"Unable to evaluate counter: {error}",
            500
        )


# =========================================================
# FINALIZE DEAL
# =========================================================

@negotiation_bp.route(
    "/finalize",
    methods=["POST"]
)
def finalize_deal():

    try:

        data = get_json_body()


        original_price = require_number(
            data,
            "original_price"
        )

        final_price = require_number(
            data,
            "final_price"
        )

        budget_max = optional_number(
            data,
            "budget_max"
        )


        result = (
            negotiation_engine.finalize_deal(
                original_price=original_price,
                final_price=final_price,
                budget_max=budget_max
            )
        )


        return jsonify(result)


    except ValueError as error:

        return error_response(
            str(error)
        )


    except Exception as error:

        return error_response(
            f"Unable to finalize deal: {error}",
            500
        )
# =========================================================
# BILLING PAGE
# =========================================================

@negotiation_bp.route(
    "/billing",
    methods=["GET"]
)
def billing_page():

    return render_template(
        "negotiation/billing.html" 
    )

# =========================================================
# GENERATE NEGOTIATION MESSAGE
# =========================================================

@negotiation_bp.route(
    "/message",
    methods=["POST"]
)
def generate_message():

    try:

        data = get_json_body()


        provider_name = (
            data.get(
                "provider_name"
            ) or
            "Service Provider"
        )

        offer_title = (
            data.get(
                "offer_title"
            ) or
            "Service"
        )

        original_price = require_number(
            data,
            "original_price"
        )

        proposed_price = require_number(
            data,
            "proposed_price"
        )

        user_requirement = (
            data.get(
                "user_requirement"
            ) or
            ""
        )


        message = (
            negotiation_engine.generate_message(
                provider_name=provider_name,
                offer_title=offer_title,
                original_price=original_price,
                proposed_price=proposed_price,
                user_requirement=user_requirement
            )
        )


        return jsonify({
            "success": True,
            "message": message
        })


    except ValueError as error:

        return error_response(
            str(error)
        )


    except Exception as error:

        return error_response(
            f"Unable to generate negotiation message: {error}",
            500
        ) 