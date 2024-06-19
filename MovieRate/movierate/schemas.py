from pydantic import BaseModel

class FilmBase(BaseModel):
    name: str
    synopsis: str
    rate: int

class FilmCreate(FilmBase):
    pass

class Film(FilmBase):
    id: int

    class Config:
        orm_mode = True
