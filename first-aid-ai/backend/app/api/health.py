from fastapi import APIRouter
from ..core.bigquery_service import get_bq_service

router = APIRouter()

@router.get("/health")
async def health_check():
    bq_service = get_bq_service()
    return {
        "status": "healthy",
        "message": "First Aid AI Backend is running",
        "persistence": "bigquery" if bq_service.client is not None else "in_memory",
        "bigquery_active": bq_service.client is not None,
        "bigquery_dataset": bq_service.dataset_id,
    }
