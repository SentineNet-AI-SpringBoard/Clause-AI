import json
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

# Load test cases
with open("test_cases.json", "r", encoding="utf-8") as f:
    tests = json.load(f)["test_cases"]

results = []

for test in tests:
    test_id = test["id"]
    endpoint = test["endpoint"]
    method = test["method"]
    payload = test.get("payload", {})

    print(f"Running {test_id} - {test['name']}")

    try:
        if method == "POST":
            response = requests.post(
                API_URL + endpoint,
                json=payload
            )
        else:
            response = requests.get(API_URL + endpoint)

        result_data = {
            "id": test_id,
            "name": test["name"],
            "status_code": response.status_code,
            "response": response.json()
        }

    except Exception as e:
        result_data = {
            "id": test_id,
            "name": test["name"],
            "status_code": "ERROR",
            "response": str(e)
        }

    results.append(result_data)

# Save results
output_filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nSaved all test results to:", output_filename)