import requests

query = """[out:json][timeout:25];
(
  node["amenity"="clinic"]["name"](30.15,-97.90,30.45,-97.60);
  node["office"="lawyer"]["name"](30.15,-97.90,30.45,-97.60);
);
out body 10;
"""

endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter"
]

for ep in endpoints:
    try:
        r = requests.post(
            ep,
            data=query,
            headers={
                "User-Agent": "XenithLeadGen/1.0 (contact@xenithsolutions.ai)",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*"
            },
            timeout=20
        )
        print(f"Endpoint: {ep} -> Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Successfully retrieved elements:", len(data.get("elements", [])))
            for el in data.get("elements", [])[:3]:
                print(" -", el.get("tags", {}).get("name"), "|", el.get("tags", {}).get("website"))
            break
        else:
            print("Response:", r.text[:200])
    except Exception as e:
        print(f"Failed {ep}: {e}")
