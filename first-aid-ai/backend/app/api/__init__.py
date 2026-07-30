from .health import router as health_router
from .auth import router as auth_router
from .questionnaire import router as questionnaire_router
from .profile import router as profile_router

__all__ = ["health_router", "auth_router", "questionnaire_router", "profile_router"]
