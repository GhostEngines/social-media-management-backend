from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator
from typing import Optional


class InsertUser(BaseModel):
    name: str
    email: str
    password: str
    timezone: Optional[str]
    # created_at: datetime
    # latest_update: datetime
    # role: str = 'User'

    @validator("timezone", pre=True, always=True)
    def set_name(cls, name):
        return name or "UTC"


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    timezone: Optional[str]
    

class ShowUser(BaseModel):
    id: Optional[str]
    name: str
    email: str
    timezone: Optional[str]
    created_at: Optional[datetime]
    latest_update: Optional[datetime]

class LoginUser(BaseModel):
    email: str
    password: str
    role: str