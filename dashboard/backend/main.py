"""FastAPI main application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import api_router
from .websocket_manager import websocket_router
from .orchestrator import orchestrator_manager
from .project_manager import project_manager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting up application...")
    try:
        await project_manager.initialize()
        logger.info("Project manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize project manager: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if orchestrator_manager.is_running():
        await orchestrator_manager.stop()

# Create FastAPI app
app = FastAPI(
    title="SplitMind Dashboard API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(websocket_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}