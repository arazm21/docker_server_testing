from sqlalchemy import Column, BigInteger, Float
from .db import Base

class WineFeatures(Base):
    __tablename__ = "wine_features"

    wine_id = Column(BigInteger, primary_key=True, index=True)
    fixed_acidity = Column(Float)
    volatile_acidity = Column(Float)
    citric_acid = Column(Float)
    residual_sugar = Column(Float)
    chlorides = Column(Float)
    free_sulfur_dioxide = Column(Float)
    total_sulfur_dioxide = Column(Float)
    density = Column(Float)
    pH = Column(Float)
    sulphates = Column(Float)
    alcohol = Column(Float)
    average_so2 = Column(Float)
