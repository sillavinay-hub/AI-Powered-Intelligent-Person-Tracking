import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.database.seed import init_db
from backend.workers.stream_manager import stream_manager
from backend.utils.logger import logger

# Import all API Routers
from backend.api.auth import router as auth_router
from backend.api.cameras import router as cameras_router
from backend.api.persons import router as persons_router
from backend.api.detections import router as detections_router
from backend.api.tracking import router as tracking_router
from backend.api.search import router as search_router
from backend.api.timeline import router as timeline_router
from backend.api.alerts import router as alerts_router
from backend.api.analytics import router as analytics_router
from backend.api.predictions import router as predictions_router
from backend.api.experiments import router as experiments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    logger.info("================================================================================")
    logger.info("Starting ResortVision AI - Intelligent Multi-Camera Person Tracking Platform")
    logger.info("================================================================================")
    logger.info(f"Resolved AI Hardware Device: {settings.resolved_device.upper()}")
    if settings.resolved_device == "cuda":
        logger.info("AI Device: NVIDIA GPU")
    else:
        logger.info("AI Device: CPU")

    # 1. Initialize & seed database (25 cameras, transitions, users)
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # 2. Initialize camera streams and background AI engine
    try:
        stream_manager.initialize_cameras()
        stream_manager.start_ai_processing()
    except Exception as e:
        logger.error(f"Stream Manager initialization error: {e}")

    yield

    # Shutdown:
    logger.info("Shutting down ResortVision AI...")
    stream_manager.stop_all()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_SUBTITLE,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for uploaded reference images
uploads_dir = str(settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Register API Routers
app.include_router(auth_router)
app.include_router(cameras_router)
app.include_router(persons_router)
app.include_router(detections_router)
app.include_router(tracking_router)
app.include_router(search_router)
app.include_router(timeline_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(experiments_router)

@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "subtitle": settings.APP_SUBTITLE,
        "status": "OPERATIONAL",
        "total_cameras": 25,
        "device": settings.resolved_device.upper(),
        "demo_mode": settings.DEMO_MODE,
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "device": settings.resolved_device.upper(),
        "ai_processing": stream_manager.is_ai_running,
        "active_streams": len(stream_manager.sources)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
