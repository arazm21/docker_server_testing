import requests
import json
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")  # adjust path as needed
host = "http://model" if os.getenv("OP_MODE") == "DOCKER" else "http://localhost"
# print(host)

class ModelClient:
    # def __init__(self, host="http://localhost", port=5000):
    def __init__(self, host=host, port=5000):

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
