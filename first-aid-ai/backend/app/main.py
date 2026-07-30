from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import health_router, auth_router, questionnaire_router, profile_router
from .core.bigquery_service import get_bq_service
from .core.config import settings

import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        bq_service = get_bq_service()
        if bq_service.client is not None:
            bq_service.create_dataset_and_tables()
            logger.info("BigQuery client initialized successfully")
        else:
            logger.warning("BigQuery client not available; running with in-memory storage")
        yield
    except RuntimeError as e:
        # Gracefully fall back to in-memory mode when Google Cloud libraries
        # are unavailable (e.g. MSYS2/MinGW local development)
        logger.warning(f"BigQuery initialization failed, falling back to in-memory storage: {e}")
        yield
    except Exception as e:
        raise RuntimeError(f"Failed to initialize application: {e}") from e


app = FastAPI(title="First Aid AI Backend", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(questionnaire_router, prefix="/api/questionnaire", tags=["questionnaire"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])

@app.get("/")
async def root():
    return {"message": "Welcome to First Aid AI Backend"}


