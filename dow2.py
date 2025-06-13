import os
import requests
import zipfile
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")

# Download model artifacts directly via REST API
run_id = "528b716f53024d0aa1c2eeeb29b5e681"
url = f"{host}/api/2.0/mlflow/artifacts/get-artifact"

params = {
    "run_id": run_id,
    "path": "model"
}

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    os.makedirs("./downloaded_models", exist_ok=True)
    with open("./downloaded_models/model.zip", "wb") as f:
        f.write(response.content)
    print("Model downloaded successfully")
else:
    print(f"Error: {response.status_code} - {response.text}")