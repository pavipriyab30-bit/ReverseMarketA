import os

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


class Config:
    """Application configuration for BESTORA FIT."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "bestora-fit-development-key")

    # Database
    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        os.path.join("database", "bestora_fit.db")
    )

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Application
    APP_NAME = "BESTORA FIT"
    APP_MOTTO = "Find. Compare. Choose Better."

    # Marketplace modes
    SERVICE_MODE = "service"
    PRODUCT_MODE = "product"

    # Default marketplace mode
    DEFAULT_MODE = SERVICE_MODE

    # AI settings
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    # Matching settings
    DEFAULT_MATCH_LIMIT = 10

    # Trust settings
    MIN_TRUST_SCORE = 0
    MAX_TRUST_SCORE = 100

    # Risk settings
    MIN_RISK_SCORE = 0
    MAX_RISK_SCORE = 100


# Active configuration object
config = Config() 