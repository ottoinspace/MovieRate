from authlib.integrations.starlette_client import OAuth #type: ignore

from json import dumps

from urllib.parse import quote_plus, urlencode

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.orm import Session
from . import models, schemas, database
from .database import SessionLocal, engine

from pydantic_settings import BaseSettings, SettingsConfigDict #type: ignore

from starlette.middleware.sessions import SessionMiddleware

from movierate.model.film import Film

models.Base.metadata.create_all(bind=engine)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env'
    )
    DOMAIN: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    SECRET_KEY: str
    AUDIENCE: str = ''

settings = Settings()

oauth = OAuth()
oauth.register(
    'auth0',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{settings.DOMAIN}/.well-known/openid-configuration',
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.mount('/static', StaticFiles(directory='static'), name='static')

def to_pretty_json(obj: dict) -> str:
    return dumps(obj, default=lambda x: dict(x), indent=4)

templates = Jinja2Templates(directory='templates')
templates.env.filters['to_pretty_json'] = to_pretty_json

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/', response_class=HTMLResponse)
def home(request: Request): 
    return templates.TemplateResponse(request=request, name='home.html')



@app.get('/login')
async def login(request: Request):
    if ( not 'id_token' in request.session ):  # it could be userinfo instead of id_token
        return await oauth.auth0.authorize_redirect(
            request,
            redirect_uri=request.url_for('callback'),
            audience=settings.AUDIENCE,
        )
    return RedirectResponse('/')

@app.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(
        url='https://'
        + settings.DOMAIN
        + '/v2/logout?'
        + urlencode(
            {
                'returnTo': request.url_for('home'),
                'client_id': settings.CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )
    request.session.clear()
    return response

@app.get('/callback')
async def callback(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    request.session['access_token'] = token['access_token']
    request.session['id_token'] = token['id_token']
    request.session['userinfo'] = token['userinfo']
    return RedirectResponse('/')

@app.get('/profile', response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request, 
        name='profile.html', 
        context={
            'request': request,
            'userinfo': request.session['userinfo']
        }
        )


@app.post("/films/", response_model=schemas.Film)
def create_film(film: schemas.FilmCreate, db: Session = Depends(get_db)):
    db_film = models.Film(name=film.name, synopsis=film.synopsis, rate=film.rate)
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

@app.get('/films/', response_model=list[schemas.Film])
def read_films(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    films = db.query(models.Film).offset(skip).limit(limit).all()
    return films

@app.delete('/films/{film_id}', response_model=schemas.Film)
def delete_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(models.Film).filter(models.Film.id == film_id).first()
    if film:
        db.delete(film)
        db.commit()
        return film
    raise HTTPException(status_code=404, detail="Film not found")
