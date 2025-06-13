from pydantic import BaseModel
from typing import Optional

class WineFeaturesBase(BaseModel):
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

class WineFeaturesCreate(WineFeaturesBase):
    wine_id: int

class WineFeatures(WineFeaturesBase):
    wine_id: int

    model_config = {
        "from_attributes": True
    }