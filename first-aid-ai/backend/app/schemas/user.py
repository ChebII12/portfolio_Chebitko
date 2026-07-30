from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    level: Optional[str] = None
    questionnaire_data: Optional[Dict[str, Any]] = None

class User(UserBase):
    id: Optional[str] = None
    level: Optional[str] = None
    registration_date: Optional[datetime] = None
    questionnaire_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

    @validator('id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

