import requests
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="../.env")  # adjust path as needed


host = "http://database" if os.getenv("OP_MODE") == "DOCKER" else "http://localhost"
# print(host)
class DatabaseClient:
    # def __init__(self, host="http://localhost", port=8000):  # container name
    def __init__(self, host=host, port=8000):  # container name

        self.base_url = f"{host}:{port}"

    def get_wine_features(self, wine_id: int) -> dict:
        response = requests.get(f"{self.base_url}/features/{wine_id}")
        response.raise_for_status()
        return response.json()
