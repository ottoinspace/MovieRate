from sqlalchemy import Column, Integer, String
from .database import Base

class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    synopsis = Column(String, index=True)
    rate = Column(Integer)