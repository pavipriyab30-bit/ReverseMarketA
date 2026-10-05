from app import app

client = app.test_client()

response = client.post(
    "/service/match",
    json={
        "requirement": "I need a laptop repair in Chennai under 1000"
    }
)

print("STATUS:", response.status_code)

data = response.get_json()

print("SUCCESS:", data.get("success"))
print("MATCH COUNT:", len(data.get("matches", [])))

for match in data.get("matches", []):
    print(
        match["provider"]["name"],
        "|",
        match["offer"]["title"],
        "|",
        match["match_score"]
    )
