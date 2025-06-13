from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import db, models, schemas, crud

models.Base.metadata.create_all(bind=db.engine)

app = FastAPI()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.get("/")
def root():
    return {"message": "Wine DB is running!"}

@app.post("/create_features/", response_model=schemas.WineFeatures)
def create_feature(features: schemas.WineFeaturesCreate, db: Session = Depends(get_db)):
    return crud.create_wine_features(db, features)

@app.get("/features/{wine_id}", response_model=schemas.WineFeatures)
def read_feature(wine_id: int, db: Session = Depends(get_db)):
    feature = crud.get_wine_features(db, wine_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Wine ID not found")
    return feature

