from database.database import get_database

connection = get_database()

rows = connection.execute(
    """
    SELECT
        p.name,
        p.category,
        o.title,
        o.price
    FROM providers p
    JOIN offers o
        ON o.provider_id = p.id
    WHERE p.category = ?
    """,
    ("Laptop Repair",)
).fetchall()

print("LAPTOP REPAIR DATASET")
print("-" * 60)

for row in rows:
    print(
        f"{row['name']} | "
        f"{row['category']} | "
        f"{row['title']} | "
        f"{row['price']}"
    )

print("-" * 60)
print("COUNT:", len(rows))

connection.close()
