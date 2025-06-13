import os
from dotenv import load_dotenv
import mlflow

# Load environment variables from .env
load_dotenv()

# Set up MLflow tracking URI
host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")

if not host or not token:
    raise Exception("Missing DATABRICKS_HOST or DATABRICKS_TOKEN")

# Set environment variables for MLflow authentication
os.environ["DATABRICKS_HOST"] = host
os.environ["DATABRICKS_TOKEN"] = token

# Set tracking URI - make sure this matches your Databricks workspace URL
mlflow.set_tracking_uri("databricks")  # Should be something like "https://your-workspace.cloud.databricks.com"

# Log the current tracking URI
print("Tracking URI:", mlflow.get_tracking_uri())

try:
    # Download the model to a specific local directory
    logged_model = 'runs:/528b716f53024d0aa1c2eeeb29b5e681/model'
    local_path = mlflow.artifacts.download_artifacts(
        artifact_uri=logged_model,
        dst_path="./downloaded_models"  # Specify local destination
    )
    
    print("Model downloaded to:", local_path)
    print("Files in downloaded model:", os.listdir(local_path))
    
except Exception as e:
    print(f"Error downloading model: {e}")