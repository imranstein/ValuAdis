import requests

# Login
r = requests.post("http://localhost:8026/api/v1/auth/login", json={"email": "admin@valuadis.com", "password": "password123"})
token = r.json().get("access_token")
print(f"Token: {token}")

# Create property
r2 = requests.post("http://localhost:8026/api/v1/properties", headers={"Authorization": f"Bearer {token}"}, json={
    "property_type": "residential",
    "municipality": "Addis Ababa",
    "address": "123 Test St, Addis Ababa",
    "coordinates": [[38.74, 9.03], [38.75, 9.03], [38.75, 9.04], [38.74, 9.04], [38.74, 9.03]]
})
print("Status Code:", r2.status_code)
print("Response:", r2.text)
