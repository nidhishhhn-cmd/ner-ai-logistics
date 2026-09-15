"""
NER AI Logistics Intelligence Platform - FastAPI Backend
Ministry of Development of North Eastern Region (MDoNER) Hackathon
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database.connection import engine, Base, SessionLocal
from app.database.seeder import seed_database
from app.models import models  # noqa - registers all models
from app.routers import auth, routes, geography, hubs, alerts, analytics, insights, feedback, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown: nothing needed


app = FastAPI(
    title="NER Logistics Intelligence Platform API",
    description="AI-powered logistics intelligence for India's North Eastern Region (MDoNER Hackathon)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS - allow frontend on any port in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(routes.router)
app.include_router(geography.router)
app.include_router(hubs.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(insights.router)
app.include_router(feedback.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "NER Logistics Intelligence Platform",
        "version": "1.0.0",
        "data_mode": "demo",
        "data_source": "Simulated NER Demo Data"
    }


@app.get("/")
def root():
    static_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return JSONResponse({
        "message": "NER Logistics Intelligence Platform API",
        "docs": "/api/docs",
        "health": "/api/health",
        "version": "1.0.0"
    })

# Mount static files after all API routes
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
