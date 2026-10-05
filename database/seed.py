
import sqlite3
import sys
from pathlib import Path


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from config import config


# =========================================================
# SERVICE PROVIDERS
# =========================================================

PROVIDERS = [

    # -----------------------------------------------------
    # HOME REPAIR
    # -----------------------------------------------------

    {
        "name": "Arun Home Services",
        "category": "Home Repair",
        "description": "Professional home repair and maintenance services.",
        "location": "Chennai",
        "phone": "9876543210",
        "email": "arunhomeservices@example.com",
        "experience_years": 8,
        "rating": 4.7,
        "review_count": 186,
        "completed_jobs": 420,
        "response_rate": 96.0,
        "verified": 1,
        "trust_score": 91.0,
    },

    {
        "name": "Chennai HomeCare",
        "category": "Home Repair",
        "description": "Affordable home maintenance, plumbing and general repair services.",
        "location": "Chennai",
        "phone": "9876543220",
        "email": "chennaihomecare@example.com",
        "experience_years": 5,
        "rating": 4.4,
        "review_count": 94,
        "completed_jobs": 210,
        "response_rate": 90.0,
        "verified": 1,
        "trust_score": 82.0,
    },

    {
        "name": "FixRight Home Solutions",
        "category": "Home Repair",
        "description": "General handyman and residential maintenance services.",
        "location": "Chennai",
        "phone": "9876543221",
        "email": "fixright@example.com",
        "experience_years": 3,
        "rating": 4.1,
        "review_count": 38,
        "completed_jobs": 75,
        "response_rate": 72.0,
        "verified": 0,
        "trust_score": 64.0,
    },


    # -----------------------------------------------------
    # LAPTOP REPAIR
    # -----------------------------------------------------

    {
        "name": "TechFix Solutions",
        "category": "Laptop Repair",
        "description": "Laptop, desktop and computer repair services.",
        "location": "Chennai",
        "phone": "9876543211",
        "email": "techfix@example.com",
        "experience_years": 6,
        "rating": 4.6,
        "review_count": 142,
        "completed_jobs": 310,
        "response_rate": 94.0,
        "verified": 1,
        "trust_score": 88.0,
    },

    {
        "name": "LaptopCare Chennai",
        "category": "Laptop Repair",
        "description": "Affordable laptop diagnostics, software troubleshooting and hardware repair.",
        "location": "Chennai",
        "phone": "9876543222",
        "email": "laptopcare@example.com",
        "experience_years": 4,
        "rating": 4.3,
        "review_count": 86,
        "completed_jobs": 175,
        "response_rate": 88.0,
        "verified": 1,
        "trust_score": 79.0,
    },

    {
        "name": "QuickLaptop Repairs",
        "category": "Laptop Repair",
        "description": "Budget laptop repair and basic computer troubleshooting services.",
        "location": "Chennai",
        "phone": "9876543223",
        "email": "quicklaptop@example.com",
        "experience_years": 2,
        "rating": 3.9,
        "review_count": 27,
        "completed_jobs": 54,
        "response_rate": 68.0,
        "verified": 0,
        "trust_score": 58.0,
    },


    # -----------------------------------------------------
    # ELECTRICAL
    # -----------------------------------------------------

    {
        "name": "Spark Electricals",
        "category": "Electrical",
        "description": "Residential electrical installation and repair services.",
        "location": "Chennai",
        "phone": "9876543212",
        "email": "sparkelectricals@example.com",
        "experience_years": 10,
        "rating": 4.8,
        "review_count": 231,
        "completed_jobs": 560,
        "response_rate": 98.0,
        "verified": 1,
        "trust_score": 94.0,
    },

    {
        "name": "BrightVolt Electrical Services",
        "category": "Electrical",
        "description": "Home electrician services including wiring, switches and electrical repairs.",
        "location": "Chennai",
        "phone": "9876543224",
        "email": "brightvolt@example.com",
        "experience_years": 7,
        "rating": 4.5,
        "review_count": 126,
        "completed_jobs": 290,
        "response_rate": 93.0,
        "verified": 1,
        "trust_score": 86.0,
    },

    {
        "name": "City Electric Works",
        "category": "Electrical",
        "description": "Local electrical repair and installation services at budget-friendly prices.",
        "location": "Chennai",
        "phone": "9876543225",
        "email": "cityelectric@example.com",
        "experience_years": 3,
        "rating": 4.0,
        "review_count": 41,
        "completed_jobs": 92,
        "response_rate": 74.0,
        "verified": 0,
        "trust_score": 61.0,
    },


    # -----------------------------------------------------
    # CLEANING
    # -----------------------------------------------------

    {
        "name": "CleanPro Chennai",
        "category": "Cleaning",
        "description": "Home deep cleaning and regular cleaning services.",
        "location": "Chennai",
        "phone": "9876543213",
        "email": "cleanpro@example.com",
        "experience_years": 5,
        "rating": 4.5,
        "review_count": 118,
        "completed_jobs": 275,
        "response_rate": 92.0,
        "verified": 1,
        "trust_score": 85.0,
    },

    {
        "name": "FreshNest Cleaning Services",
        "category": "Cleaning",
        "description": "Professional apartment, kitchen and bathroom cleaning services.",
        "location": "Chennai",
        "phone": "9876543226",
        "email": "freshnest@example.com",
        "experience_years": 4,
        "rating": 4.3,
        "review_count": 82,
        "completed_jobs": 160,
        "response_rate": 89.0,
        "verified": 1,
        "trust_score": 78.0,
    },

    {
        "name": "SparkleHome Cleaners",
        "category": "Cleaning",
        "description": "Budget-friendly home cleaning and basic deep-cleaning services.",
        "location": "Chennai",
        "phone": "9876543227",
        "email": "sparklehome@example.com",
        "experience_years": 2,
        "rating": 4.0,
        "review_count": 31,
        "completed_jobs": 67,
        "response_rate": 70.0,
        "verified": 0,
        "trust_score": 59.0,
    },


    # -----------------------------------------------------
    # PACKERS AND MOVERS
    # -----------------------------------------------------

    {
        "name": "QuickMove Packers",
        "category": "Packers and Movers",
        "description": "Local and domestic moving and packing services.",
        "location": "Chennai",
        "phone": "9876543214",
        "email": "quickmove@example.com",
        "experience_years": 7,
        "rating": 4.4,
        "review_count": 97,
        "completed_jobs": 190,
        "response_rate": 89.0,
        "verified": 1,
        "trust_score": 82.0,
    },

    {
        "name": "SafeShift Movers",
        "category": "Packers and Movers",
        "description": "House shifting, packing, loading and transportation services.",
        "location": "Chennai",
        "phone": "9876543228",
        "email": "safeshift@example.com",
        "experience_years": 6,
        "rating": 4.6,
        "review_count": 135,
        "completed_jobs": 260,
        "response_rate": 94.0,
        "verified": 1,
        "trust_score": 87.0,
    },

    {
        "name": "BudgetMove Chennai",
        "category": "Packers and Movers",
        "description": "Affordable local shifting and basic packing services.",
        "location": "Chennai",
        "phone": "9876543229",
        "email": "budgetmove@example.com",
        "experience_years": 3,
        "rating": 4.0,
        "review_count": 35,
        "completed_jobs": 71,
        "response_rate": 73.0,
        "verified": 0,
        "trust_score": 60.0,
    },
]


# =========================================================
# SERVICE OFFERS
# =========================================================

OFFERS = [

    # -----------------------------------------------------
    # HOME REPAIR
    # -----------------------------------------------------

    {
        "provider": "Arun Home Services",
        "title": "Home Repair Visit",
        "description": "Inspection and general home repair service.",
        "category": "Home Repair",
        "price": 499.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.7,
    },

    {
        "provider": "Chennai HomeCare",
        "title": "Home Maintenance Visit",
        "description": "Affordable inspection and general household maintenance.",
        "category": "Home Repair",
        "price": 399.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.4,
    },

    {
        "provider": "FixRight Home Solutions",
        "title": "Budget Home Repair",
        "description": "Basic handyman inspection and repair service.",
        "category": "Home Repair",
        "price": 299.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.1,
    },


    # -----------------------------------------------------
    # LAPTOP REPAIR
    # -----------------------------------------------------

    {
        "provider": "TechFix Solutions",
        "title": "Laptop Diagnostic and Repair",
        "description": "Laptop diagnosis, hardware and software repair.",
        "category": "Laptop Repair",
        "price": 699.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.6,
    },

    {
        "provider": "LaptopCare Chennai",
        "title": "Laptop Service and Diagnosis",
        "description": "Laptop inspection, software troubleshooting and basic hardware repair.",
        "category": "Laptop Repair",
        "price": 549.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.3,
    },

    {
        "provider": "QuickLaptop Repairs",
        "title": "Budget Laptop Repair",
        "description": "Basic laptop troubleshooting and repair at an affordable price.",
        "category": "Laptop Repair",
        "price": 399.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 3.9,
    },


    # -----------------------------------------------------
    # ELECTRICAL
    # -----------------------------------------------------

    {
        "provider": "Spark Electricals",
        "title": "Electrical Repair Visit",
        "description": "Electrical inspection and repair for home issues.",
        "category": "Electrical",
        "price": 399.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.8,
    },

    {
        "provider": "BrightVolt Electrical Services",
        "title": "Home Electrical Service",
        "description": "Electrical inspection, switch repair and wiring support.",
        "category": "Electrical",
        "price": 349.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.5,
    },

    {
        "provider": "City Electric Works",
        "title": "Budget Electrician Visit",
        "description": "Basic electrical inspection and household repair.",
        "category": "Electrical",
        "price": 249.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.0,
    },


    # -----------------------------------------------------
    # CLEANING
    # -----------------------------------------------------

    {
        "provider": "CleanPro Chennai",
        "title": "Home Deep Cleaning",
        "description": "Complete deep cleaning for residential spaces.",
        "category": "Cleaning",
        "price": 1499.0,
        "delivery_time": "Same day",
        "availability": "available",
        "rating": 4.5,
    },

    {
        "provider": "FreshNest Cleaning Services",
        "title": "Apartment Deep Cleaning",
        "description": "Professional cleaning for apartments, kitchens and bathrooms.",
        "category": "Cleaning",
        "price": 1299.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.3,
    },

    {
        "provider": "SparkleHome Cleaners",
        "title": "Budget Home Cleaning",
        "description": "Affordable basic home cleaning service.",
        "category": "Cleaning",
        "price": 999.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.0,
    },


    # -----------------------------------------------------
    # PACKERS AND MOVERS
    # -----------------------------------------------------

    {
        "provider": "QuickMove Packers",
        "title": "Local Moving Package",
        "description": "Packing, loading and local transportation.",
        "category": "Packers and Movers",
        "price": 2999.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.4,
    },

    {
        "provider": "SafeShift Movers",
        "title": "Premium House Shifting",
        "description": "Professional packing, loading, transportation and unloading.",
        "category": "Packers and Movers",
        "price": 3999.0,
        "delivery_time": "1 day",
        "availability": "available",
        "rating": 4.6,
    },

    {
        "provider": "BudgetMove Chennai",
        "title": "Budget Local Shifting",
        "description": "Affordable packing and local transportation for small moves.",
        "category": "Packers and Movers",
        "price": 2299.0,
        "delivery_time": "2 days",
        "availability": "available",
        "rating": 4.0,
    },
]


# =========================================================
# SEED DATABASE
# =========================================================

def seed_database():
    """Insert BESTORA FIT service provider and offer data."""

    database_path = PROJECT_ROOT / config.DATABASE_PATH

    connection = sqlite3.connect(database_path)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Clear existing service seed data.
        # The complete dataset is recreated below.
        connection.execute("DELETE FROM offers")
        connection.execute("DELETE FROM providers")

        provider_ids = {}

        # -------------------------------------------------
        # INSERT PROVIDERS
        # -------------------------------------------------

        for provider in PROVIDERS:

            cursor = connection.execute(
                """
                INSERT INTO providers (
                    name,
                    category,
                    description,
                    location,
                    phone,
                    email,
                    experience_years,
                    rating,
                    review_count,
                    completed_jobs,
                    response_rate,
                    verified,
                    trust_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider["name"],
                    provider["category"],
                    provider["description"],
                    provider["location"],
                    provider["phone"],
                    provider["email"],
                    provider["experience_years"],
                    provider["rating"],
                    provider["review_count"],
                    provider["completed_jobs"],
                    provider["response_rate"],
                    provider["verified"],
                    provider["trust_score"],
                ),
            )

            provider_ids[provider["name"]] = cursor.lastrowid


        # -------------------------------------------------
        # INSERT OFFERS
        # -------------------------------------------------

        for offer in OFFERS:

            provider_id = provider_ids[offer["provider"]]

            connection.execute(
                """
                INSERT INTO offers (
                    provider_id,
                    title,
                    description,
                    category,
                    price,
                    delivery_time,
                    availability,
                    rating
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider_id,
                    offer["title"],
                    offer["description"],
                    offer["category"],
                    offer["price"],
                    offer["delivery_time"],
                    offer["availability"],
                    offer["rating"],
                ),
            )


        connection.commit()


        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        print(
            f"Seeded {len(PROVIDERS)} providers "
            f"and {len(OFFERS)} offers."
        )

        print("\nProviders by category:")

        rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM providers
            GROUP BY category
            ORDER BY category
            """
        ).fetchall()

        for row in rows:
            print(f"  {row[0]}: {row[1]}")


        print("\nOffers by category:")

        rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM offers
            GROUP BY category
            ORDER BY category
            """
        ).fetchall()

        for row in rows:
            print(f"  {row[0]}: {row[1]}")


    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
