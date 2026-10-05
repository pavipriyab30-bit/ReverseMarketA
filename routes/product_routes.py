from flask import Blueprint, jsonify, render_template, request

from services.product.deal_optimizer import deal_optimizer
from services.product.product_matcher import product_matcher
from services.product.product_requirement_parser import (
    product_requirement_parser,
)
from services.product.product_search import product_search


product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/product",
)


# =========================================================
# PRODUCT PAGES
# =========================================================

@product_bp.route("/", methods=["GET"])
def product_page():
    """Render the Product Mode requirement page."""

    return render_template(
        "product/requirement.html"
    )


@product_bp.route("/results", methods=["GET"])
def product_results_page():
    """Render the Product Mode results page."""

    return render_template(
        "product/results.html"
    )


@product_bp.route("/analyzing", methods=["GET"])
def product_analyzing_page():
    """Render the Product Mode analyzing page."""

    return render_template(
        "product/analyzing.html"
    )


# =========================================================
# PRODUCT SEARCH API
# =========================================================

@product_bp.route("/search", methods=["POST"])
def search_products():
    """Search products using structured or natural-language input."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON.",
        }), 400

    try:
        raw_requirement = str(
            data.get(
                "requirement",
                data.get("query", ""),
            )
        ).strip()

        if not raw_requirement:
            return jsonify({
                "success": False,
                "error": "Product requirement cannot be empty.",
            }), 400

        parsed_requirement = (
            product_requirement_parser.parse(
                raw_requirement
            )
        )

        products = product_search.search(
            query=parsed_requirement.get(
                "query",
                raw_requirement,
            ),
            category=parsed_requirement.get(
                "category"
            ),
            budget_min=parsed_requirement.get(
                "budget_min"
            ),
            budget_max=parsed_requirement.get(
                "budget_max"
            ),
            preferred_brands=parsed_requirement.get(
                "preferred_brands",
                [],
            ),
            required_features=parsed_requirement.get(
                "required_features",
                [],
            ),
            limit=int(
                data.get("limit", 20)
            ),
        )

        return jsonify({
            "success": True,
            "requirement": {
                "original_text": raw_requirement,
                **parsed_requirement,
            },
            "products": products,
            "count": len(products),
        })

    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "Unable to search products.",
            "details": str(exc),
        }), 500


# =========================================================
# PRODUCT MATCHING API
# =========================================================

@product_bp.route("/match", methods=["POST"])
def match_products():
    """
    Convert the user's natural-language requirement into
    structured requirements and find the best products.
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON.",
        }), 400

    try:
        raw_requirement = str(
            data.get(
                "requirement",
                data.get("query", ""),
            )
        ).strip()

        if not raw_requirement:
            return jsonify({
                "success": False,
                "error": "Product requirement cannot be empty.",
            }), 400

        parsed_requirement = (
            product_requirement_parser.parse(
                raw_requirement
            )
        )

        matches = product_matcher.find_matches(
            requirement=parsed_requirement,
            limit=int(
                data.get("limit", 10)
            ),
        )

        return jsonify({
            "success": True,
            "requirement": {
                "original_text": raw_requirement,
                **parsed_requirement,
            },
            "matches": matches,
            "match_count": len(matches),
        })

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "Unable to match products.",
            "details": str(exc),
        }), 500


# =========================================================
# SINGLE PRODUCT API
# =========================================================

@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Return a single product."""

    try:
        product = product_search.get_by_id(
            product_id
        )

        if product is None:
            return jsonify({
                "success": False,
                "error": "Product not found.",
            }), 404

        return jsonify({
            "success": True,
            "product": product,
        })

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "Unable to retrieve product.",
            "details": str(exc),
        }), 500

@product_bp.route("/billing", methods=["GET"])
def product_billing_page():
    return render_template("product/billing.html") 
# =========================================================
# DEAL OPTIMIZATION API
# =========================================================

@product_bp.route("/deal", methods=["POST"])
def optimize_deal():
    """Calculate the deal quality of a product."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON.",
        }), 400

    product = data.get("product")

    if not isinstance(product, dict):
        return jsonify({
            "success": False,
            "error": "The 'product' field must be an object.",
        }), 400

    try:
        budget_max = data.get("budget_max")

        if budget_max is not None:
            budget_max = float(budget_max)

        optimized_product = deal_optimizer.optimize(
            product=product,
            budget_max=budget_max,
        )

        return jsonify({
            "success": True,
            "deal": optimized_product,
        })

    except (TypeError, ValueError) as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 400

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": "Unable to optimize the deal.",
            "details": str(exc),
        }), 500 