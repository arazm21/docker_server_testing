from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from typing import Optional
import uvicorn

# Load the model once when the app starts
try:
    with open('./downloaded_models/model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Create FastAPI app
app = FastAPI(
    title="Wine Quality Prediction API",
    description="API for predicting wine quality using machine learning",
    version="1.0.0"
)

# Define input data model
class WineFeatures(BaseModel):
    real_time_measurement: float
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float
    average_so2: float


# Define response model
class PredictionResponse(BaseModel):
    prediction: float
    message: str

@app.get("/")
async def root():
    return {"message": "Wine Quality Prediction API", "status": "running"}

@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
async def predict_wine_quality(features: WineFeatures):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Convert input to DataFrame
        input_data = {
            "real_time_measurement": [features.real_time_measurement],            
            "fixed_acidity": [features.fixed_acidity],
            "volatile_acidity": [features.volatile_acidity],
            "citric_acid": [features.citric_acid],
            "residual_sugar": [features.residual_sugar],
            "chlorides": [features.chlorides],
            "free_sulfur_dioxide": [features.free_sulfur_dioxide],
            "total_sulfur_dioxide": [features.total_sulfur_dioxide],
            "density": [features.density],
            "pH": [features.pH],
            "sulphates": [features.sulphates],
            "alcohol": [features.alcohol],
            "average_so2": [features.average_so2],

        }
        
        input_df = pd.DataFrame(input_data)
        
        # Make prediction
        prediction = model.predict(input_df)
        
        return PredictionResponse(
            prediction=float(prediction[0]),
            message="Prediction successful"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

# Example endpoint to test with your specific data
@app.get("/predict/example")
async def predict_example():
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Your example data
        input_data = {
            "real_time_measurement": [3.1],
            "fixed_acidity": [7.4],
            "volatile_acidity": [0.7],
            "citric_acid": [0.0],
            "residual_sugar": [1.9],
            "chlorides": [0.076],
            "free_sulfur_dioxide": [11],
            "total_sulfur_dioxide": [34],
            "density": [0.9978],
            "pH": [3.51],
            "sulphates": [0.56],
            "alcohol": [9.4],
            "average_so2": [22.5],
        }
        
        input_df = pd.DataFrame(input_data)
        prediction = model.predict(input_df)
        
        return {
            "prediction": float(prediction[0]),
            "input_data": input_data,
            "message": "Example prediction successful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    
    
    
# {
#   "real_time_measurement": 3.1,
#   "fixed_acidity": 7.4,
#   "volatile_acidity": 0.7,
#   "citric_acid": 0.0,
#   "residual_sugar": 1.9,
#   "chlorides": 0.076,
#   "free_sulfur_dioxide": 11,
#   "total_sulfur_dioxide": 34,
#   "density": 0.9978,
#   "pH": 3.51,
#   "sulphates": 0.56,
#   "alcohol": 9.4,
#   "average_so2": 22.5
# }

# conda config --set ssl_verify False
