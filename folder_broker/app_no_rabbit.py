from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from shared.database_client import DatabaseClient
from shared.model_client import ModelClient
from shared.predictor import WineQualityPredictor
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
import logging
logging.basicConfig(level=logging.INFO)
# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
db_client = DatabaseClient()
model_client = ModelClient()
predictor = WineQualityPredictor(db_client, model_client)


templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.get("/predict")
def predict(wine_id: int = Query(...), real_time_measurement: float = Query(...)):
    try:
        result = predictor.predict_quality(wine_id, real_time_measurement)
        logging.info(result)
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


