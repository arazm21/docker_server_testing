import requests
import json

class ModelClient:
    # def __init__(self, host="http://localhost", port=5000):
    def __init__(self, host="http://model", port=5000):

        self.url = f"{host}:{port}/invocations"
        self.headers = {"Content-Type": "application/json"}

    def predict(self, features: dict) -> float:
        payload = {
            "inputs": [features]  # wrap in list for batch compatibility
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()
