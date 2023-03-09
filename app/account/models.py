from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# INDIVIDUAL ACCOUNT MODEL

class IndividualAccount(BaseModel):
    type: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    org_id: Optional[str]
    account_id: str
    created: datetime
    is_active: Optional[bool] = True
    # owner: str
    

class Account(BaseModel):
    accounts: List[IndividualAccount] = []


class InsertIndividualAccount(BaseModel):
    # type: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    org_id: Optional[str]
    is_active: Optional[bool] = True


class UpdateIndividualAccount(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    org_id: Optional[str]
    is_active: Optional[bool] = True


class ShowIndividualAccount(BaseModel):
    type: str
    org_id: Optional[str]
    account_id: str
    created: Optional[datetime]
    is_active: bool = True
