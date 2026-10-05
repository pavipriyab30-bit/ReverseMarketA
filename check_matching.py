from services.matching_engine import matching_engine

result = matching_engine.find_matches(
    {
        "category": "Laptop Repair",
        "budget_max": 1000,
        "location": "Chennai"
    }
)

print("MATCHING ENGINE RESULTS")
print("-" * 60)
print("COUNT:", len(result))

for item in result:
    print(
        item["provider"]["name"],
        "|",
        item["offer"]["title"],
        "| Score:",
        item["match_score"]
    )

print("-" * 60)
