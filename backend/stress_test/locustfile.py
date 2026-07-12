"""
ValuAdis API Stress Testing Suite

Comprehensive load testing for Ethiopian Property Valuation Platform.
Includes an auth-ready path so authenticated workloads can run against
real business endpoints in a local dev environment.
"""

from locust import HttpUser, task, between
import random
import os
from uuid import uuid4
from datetime import datetime


class ValuAdisUser(HttpUser):
    """
    Simulates Ethiopian property valuer using the ValuAdis API.
    """

    wait_time = between(1, 3)

    def on_start(self):
        print(f"👤 Starting valuer user for {self.environment.parsed_options.host}")
        self.access_token = self._resolve_access_token()
        if not self.access_token:
            print("⚠️  Could not authenticate; auth-gated calculations will be skipped")

    @property
    def auth_headers(self):
        if not self.access_token:
            return None
        return {"Authorization": f"Bearer {self.access_token}"}

    def _normalize_response_token(self, payload):
        return (
            payload.get("data", {}).get("access_token")
            if isinstance(payload, dict)
            else None
        )

    def _register_and_login(self):
        email = os.getenv("VALUADIS_STRESS_EMAIL")
        password = os.getenv("VALUADIS_STRESS_PASSWORD")

        if email and password:
            existing_token = self._login(email, password)
            if existing_token:
                return existing_token

        random_id = uuid4().hex[:8]
        generated_email = f"locust-{random_id}@valuadis.test"
        generated_password = password or "LoadTest@1234"
        generated_phone = f"+2519{random.randint(10000000, 99999999)}"
        generated_license = f"AD-{random.randint(1000000000, 9999999999)}"

        register_payload = {
            "email": generated_email,
            "full_name": "Load Test Valuer",
            "phone": generated_phone,
            "password": generated_password,
            "municipality": "Addis Ababa",
            "license_number": generated_license,
        }

        register_response = self.client.post(
            "/api/v1/auth/register",
            json=register_payload,
        )

        if register_response.status_code == 200:
            return self._normalize_response_token(register_response.json())

        # If registration fails for any reason, attempt explicit login path.
        return self._login(email or generated_email, generated_password)

    def _login(self, email, password):
        login_payload = {"email": email, "password": password}
        login_response = self.client.post("/api/v1/auth/login", json=login_payload)
        if login_response.status_code != 200:
            return None
        return self._normalize_response_token(login_response.json())

    def _resolve_access_token(self):
        env_token = os.getenv("VALUADIS_STRESS_TOKEN")
        if env_token:
            return env_token
        return self._register_and_login()

    def _post(self, path, payload):
        if not self.auth_headers:
            return None
        return self.client.post(path, json=payload, headers=self.auth_headers, catch_response=True)

    @task(3)
    def health_check(self):
        self.client.get("/health")
        self.client.get("/api/v1/health/ping")

    @task(2)
    def api_documentation(self):
        self.client.get("/docs")
        self.client.get("/openapi.json")

    @task(1)
    def root_endpoint(self):
        self.client.get("/")

    def _validate_calculation_response(self, response):
        if response.status_code != 200:
            response.failure(f"HTTP {response.status_code}")
            return

        payload = response.json()
        data = payload.get("data", payload)
        market_value = data.get("market_value", 0)
        taxable_value = data.get("taxable_value", 0)
        expected_taxable = market_value * 0.25

        if abs(taxable_value - expected_taxable) < 1:
            response.success()
        else:
            response.failure(
                f"Ethiopian tax compliance failed: {taxable_value} vs {expected_taxable}"
            )

    @task(5)
    def valuation_calculation(self):
        if not self.auth_headers:
            return

        ethiopian_scenarios = [
            {
                "property_type": "residential",
                "municipality": "Addis Ababa",
                "area_sqm": random.uniform(50, 500),
                "coordinates": self.generate_ethiopian_coordinates("addis_ababa"),
                "property_id": random.randint(1, 1000),
            },
            {
                "property_type": "commercial",
                "municipality": "Dire Dawa",
                "area_sqm": random.uniform(100, 1000),
                "coordinates": self.generate_ethiopian_coordinates("dire_dawa"),
                "property_id": random.randint(1, 1000),
            },
            {
                "property_type": "agricultural",
                "municipality": "Mekelle",
                "area_sqm": random.uniform(1000, 10000),
                "coordinates": self.generate_ethiopian_coordinates("mekelle"),
                "property_id": random.randint(1, 1000),
            },
            {
                "property_type": "residential",
                "municipality": "Hawassa",
                "area_sqm": random.uniform(80, 300),
                "coordinates": self.generate_ethiopian_coordinates("hawassa"),
                "property_id": random.randint(1, 1000),
            },
        ]

        with self._post("/api/v1/valuations/calculate", random.choice(ethiopian_scenarios)) as response:
            self._validate_calculation_response(response)

    def generate_ethiopian_coordinates(self, municipality):
        coords = {
            "addis_ababa": (38.7578, 9.0320),
            "dire_dawa": (41.8667, 9.6000),
            "mekelle": (39.4733, 13.4967),
            "hawassa": (38.4833, 7.0583),
            "bahirdar": (37.3897, 11.5945),
            "gondar": (37.4667, 12.6000),
            "jimma": (36.8333, 7.6667),
        }

        base_lat, base_lon = coords.get(municipality, coords["addis_ababa"])
        polygon = []
        for _ in range(5):
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            polygon.append([base_lon + lon_offset, base_lat + lat_offset])
        polygon.append(polygon[0])
        return polygon


class EthiopianValuerUser(ValuAdisUser):
    """
    Specialized user for valuation-only workload.
    """

    wait_time = between(2, 5)

    @task(8)
    def complex_valuation_calculations(self):
        if not self.auth_headers:
            return

        complex_scenarios = [
            {
                "property_type": "commercial",
                "municipality": "Addis Ababa",
                "area_sqm": random.uniform(1000, 5000),
                "coordinates": self.generate_complex_polygon("addis_ababa"),
                "property_id": random.randint(1000, 2000),
            },
            {
                "property_type": "agricultural",
                "municipality": "Mekelle",
                "area_sqm": random.uniform(10000, 50000),
                "coordinates": self.generate_complex_polygon("mekelle"),
                "property_id": random.randint(1000, 2000),
            },
            {
                "property_type": "commercial",
                "municipality": "Dire Dawa",
                "area_sqm": random.uniform(2000, 10000),
                "coordinates": self.generate_complex_polygon("dire_dawa"),
                "property_id": random.randint(1000, 2000),
            },
        ]

        with self._post("/api/v1/valuations/calculate", random.choice(complex_scenarios)) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return

            payload = response.json()
            data = payload.get("data", payload)
            market_value = data.get("market_value", 0)
            taxable_value = data.get("taxable_value", 0)
            base_rate = data.get("base_rate", 0)
            multiplier = data.get("multiplier", 0)

            checks = [
                abs(taxable_value - (market_value * 0.25)) < 1,
                base_rate > 0,
                multiplier > 0,
                market_value > 0,
            ]

            if all(checks):
                response.success()
            else:
                response.failure(f"Compliance check failed: {checks}")

    def generate_complex_polygon(self, municipality):
        coords = {
            "addis_ababa": (38.7578, 9.0320),
            "dire_dawa": (41.8667, 9.6000),
            "mekelle": (39.4733, 13.4967),
        }

        base_lat, base_lon = coords.get(municipality, coords["addis_ababa"])
        polygon = []
        for i in range(8):
            angle = (i * 45) * 3.14159 / 180
            radius = random.uniform(0.005, 0.02)
            lat_offset = radius * 0.009 * 111
            lon_offset = radius * 0.009 * 111 / 37

            lat = base_lat + lat_offset * (1 if i % 2 == 0 else -1)
            lon = base_lon + lon_offset * (1 if i % 3 == 0 else -1)
            polygon.append([lon, lat])

        polygon.append(polygon[0])
        return polygon


class SystemAdminUser(HttpUser):
    """
    Simulates system administrator checks.
    """

    wait_time = between(5, 10)

    @task(4)
    def system_health_monitoring(self):
        health_endpoints = [
            "/health",
            "/api/v1/health/ping",
            "/api/v1/health/database",
            "/api/v1/health/redis",
            "/api/v1/health/full",
        ]

        for endpoint in health_endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Health check failed: {endpoint}")

    @task(3)
    def api_documentation_access(self):
        for endpoint in ["/docs", "/redoc", "/openapi.json"]:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Documentation failed: {endpoint}")

    @task(2)
    def system_information(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Root endpoint failed")


class LoadTestUser(ValuAdisUser):
    """High-frequency valuation workload for stress tests."""

    wait_time = between(0.5, 2)

    @task(10)
    def rapid_valuation_calculations(self):
        if not self.auth_headers:
            return

        quick_data = {
            "property_id": random.randint(1, 10000),
            "property_type": random.choice(["residential", "commercial", "agricultural"]),
            "municipality": random.choice(["Addis Ababa", "Dire Dawa", "Mekelle", "Hawassa"]),
            "area_sqm": random.uniform(50, 1000),
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]],
        }

        with self._post("/api/v1/valuations/calculate", quick_data) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Load test failed: HTTP {response.status_code}")


class WebsiteUser(ValuAdisUser):
    """Mixed user for health and valuation traffic."""

    wait_time = between(1, 3)

    @task(3)
    def valuation_calculation(self):
        if not self.auth_headers:
            return

        data = {
            "property_id": random.randint(1, 1000),
            "property_type": random.choice(["residential", "commercial", "agricultural"]),
            "municipality": random.choice(["Addis Ababa", "Dire Dawa", "Mekelle"]),
            "area_sqm": random.uniform(100, 500),
            "coordinates": [[38.7578, 9.0320], [38.7580, 9.0320], [38.7580, 9.0318], [38.7578, 9.0318], [38.7578, 9.0320]],
        }

        with self._post("/api/v1/valuations/calculate", data) as response:
            self._validate_calculation_response(response)

    @task(2)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def documentation(self):
        self.client.get("/docs")
