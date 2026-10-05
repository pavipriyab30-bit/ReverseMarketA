from flask import Blueprint, jsonify, render_template, request

from config import config
from services.matching_engine import matching_engine
from services.requirement_parser import requirement_parser


service_bp = Blueprint(
    "service",
    __name__,
    url_prefix="/service",
)


# =========================================================
# SERVICE PAGES
# =========================================================

@service_bp.route("/", methods=["GET"])
def service_page():
    """Render the Service Mode requirement page."""

    return render_template(
        "service/requirement.html"
    )


@service_bp.route("/results", methods=["GET"])
def service_results_page():
    """Render the Service Mode results page."""

    return render_template(
        "service/results.html"
    )


@service_bp.route("/provider", methods=["GET"])
def service_provider_page():
    """Render the detailed provider page."""

    return render_template(
        "service/provider.html"
    )


# =========================================================
# SERVICE MATCHING API
# =========================================================

@service_bp.route("/match", methods=["POST"])
def match_service():
    """
    Match a user's service requirement with providers.

    Expected JSON:

    {
        "requirement":
            "I need an electrician in Chennai today under 500"
    }
    """

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "error": "Request body must be valid JSON.",
            }
        ), 400


    requirement_text = data.get("requirement")


    if not isinstance(requirement_text, str):
        return jsonify(
            {
                "success": False,
                "error": "The 'requirement' field is required.",
            }
        ), 400


    requirement_text = requirement_text.strip()


    if not requirement_text:
        return jsonify(
            {
                "success": False,
                "error": "Requirement cannot be empty.",
            }
        ), 400


    try:

        # -------------------------------------------------
        # 1. Understand the requirement
        # -------------------------------------------------

        parsed_requirement = (
            requirement_parser.parse(
                requirement_text
            )
        )


        # -------------------------------------------------
        # 2. Find and rank providers
        # -------------------------------------------------

        matches = (
            matching_engine.find_matches(
                parsed_requirement,
                limit=config.DEFAULT_MATCH_LIMIT,
            )
        )


        # -------------------------------------------------
        # 3. Return complete result
        # -------------------------------------------------

        return jsonify(
            {
                "success": True,

                "requirement": {
                    "original_text":
                        requirement_text,

                    **parsed_requirement,
                },

                "matches": matches,

                "match_count":
                    len(matches),
            }
        )


    except ValueError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400


    except Exception as exc:

        return jsonify(
            {
                "success": False,
                "error":
                    "Unable to process the service request.",

                "details":
                    str(exc),
            }
        ), 500


# =========================================================
# PROVIDER API
# =========================================================

@service_bp.route("/providers", methods=["GET"])
def get_providers():
    """
    Return all available providers.

    Useful for development and testing.
    """

    from database.database import get_database
    from models.provider import Provider


    connection = get_database()


    try:

        rows = connection.execute(
            """
            SELECT *
            FROM providers
            ORDER BY
                trust_score DESC,
                rating DESC
            """
        ).fetchall()


        providers = [
            Provider.from_row(row).to_dict()
            for row in rows
        ]


        return jsonify(
            {
                "success": True,
                "providers": providers,
                "count": len(providers),
            }
        )


    finally:

        connection.close() 