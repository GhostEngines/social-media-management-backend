from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import Form


# FORM FOR TASK UPLOAD - ITEMFORM

class ItemForm(BaseModel):

    scheduled: Optional[datetime] = datetime.now()
    comments: Optional[str]
    text: Optional[str]
    description: Optional[str]
    category : Optional[int]

    @classmethod
    def as_form(cls, comments: str = Form(...), text: str = Form(...), description = Form(...), category = Form(...), scheduled: datetime = datetime.now()) -> 'ItemForm':
        return cls(comments=comments, text=text, description=description, category=category, scheduled=scheduled)


# TASK MODEL

class IndividualTask(BaseModel):
    task_id: Optional[str]
    name: str
    created: datetime
    text: str
    file: str
    scheduled: datetime
    is_active: Optional[bool] = True
    owner: str

class InsertTask(BaseModel):
    is_active: Optional[bool] = True
    scheduled: datetime
    owner: str

class UpdateTask(BaseModel):
    is_active: Optional[bool] = True
    scheduled: datetime
    
class ShowTask(BaseModel):
    id: str
    task_id: Optional[str]
    created: datetime
    updated: datetime
    scheduled: datetime
    owner: str
    is_active: bool = True
    text: str
    comments: str
    file: str
    description: str
    category : int
