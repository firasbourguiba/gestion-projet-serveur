"""Point d'entrée de l'API : configuration FastAPI, CORS et démarrage."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import Base, engine, SessionLocal
from app import models, auth
from app.routes import auth as auth_routes
from app.routes import projects as projects_routes
from app.routes import tasks as tasks_routes
from app.routes import participants as participants_routes

app = FastAPI(title="Gestion de projet - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gestion centralisée des erreurs : toujours répondre avec un JSON {"detail": "..."}
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Données envoyées invalides", "errors": exc.errors()},
    )


app.include_router(auth_routes.router)
app.include_router(projects_routes.router)
app.include_router(tasks_routes.router)
app.include_router(participants_routes.router)


def create_demo_account():
    """Crée un compte de démonstration au premier démarrage s'il n'existe pas déjà."""
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == "demo@demo.com").first()
        if not existing:
            demo_user = models.User(
                email="demo@demo.com",
                password_hash=auth.hash_password("demo1234"),
                name="Démo",
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    create_demo_account()


@app.get("/")
def root():
    return {"message": "API de gestion de projet, voir /docs pour la documentation"}
