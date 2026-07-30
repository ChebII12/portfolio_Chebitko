from typing import List, Literal, Optional
from pydantic import BaseModel, Field

UserLevel = Literal["beginner", "intermediate", "expert"]


class QuestionnaireAnalyzeRequest(BaseModel):
    user_id: Optional[str] = None
    answers: List[str]


class QuestionnaireAnalyzeResponse(BaseModel):
    level: UserLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    classification_source: str
    message: str

