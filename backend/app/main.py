from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, auth, queues, realtime, tenants
from app.core.config import settings
from app.db.session import create_database
from app.seed import seed_initial_data


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_database()
    seed_initial_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(queues.router, prefix="/queues", tags=["queues"])
app.include_router(realtime.router, prefix="/realtime", tags=["realtime"])

