from services.matching_engine import matching_engine

print("AVAILABLE METHODS")
print("-" * 60)

for name in dir(matching_engine):
    if not name.startswith("_"):
        print(name)

print("-" * 60)
