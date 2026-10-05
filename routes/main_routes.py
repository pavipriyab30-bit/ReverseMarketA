from flask import Blueprint, jsonify, render_template


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Render the BESTORA FIT homepage."""

    return render_template("index.html")


@main_bp.route("/health")
def health():
    """Application health-check endpoint."""

    return jsonify(
        {
            "success": True,
            "application": "BESTORA FIT",
            "status": "running",
        }
    ) 