from sqlalchemy.orm import Session
from . import models, schemas

def get_wine_features(db: Session, wine_id: int):
    return db.query(models.WineFeatures).filter(models.WineFeatures.wine_id == wine_id).first()

def create_wine_features(db: Session, features: schemas.WineFeaturesCreate):
    db_record = models.WineFeatures(**features.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
