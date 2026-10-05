from flask import Flask

from config import config
from database.database import init_database
from routes.main_routes import main_bp
from routes.service_routes import service_bp
from routes.negotiation_routes import negotiation_bp
from routes.product_routes import product_bp 


def create_app():
    """Create and configure the BESTORA FIT Flask application."""

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Initialize the database.
    init_database()

    # Register application routes.
    app.register_blueprint(main_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(negotiation_bp)
    app.register_blueprint(product_bp) 

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    ) 