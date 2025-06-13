import requests
# In DatabaseClient
class DatabaseClient:
    # def __init__(self, host="http://localhost", port=8000):  # container name
    def __init__(self, host="http://database", port=8000):  # container name

        self.base_url = f"{host}:{port}"

    def get_wine_features(self, wine_id: int) -> dict:
        response = requests.get(f"{self.base_url}/features/{wine_id}")
        response.raise_for_status()
        return response.json()
