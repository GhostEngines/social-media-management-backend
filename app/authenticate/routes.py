from fastapi import APIRouter, Depends, HTTPException, status
from app.authenticate.services import create_access_token, Hash
from fastapi.security import OAuth2PasswordRequestForm
from app.config.db import user_collection
from app.config.appConstants import appConstants

router = APIRouter(
    tags=['Authentication'],
)

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({'email': request.username})

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid credentials')

    # Generate JWT Token and return
    if not Hash.verify(user['password'], request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid credentials')

    access_token = create_access_token(data={"username": request.username, "user_id": str(user['_id'])})

    return {"access_token": access_token, "token_type": "bearer", "expires_in": appConstants.access_token_expire_minutes, "id": str(user['_id'])}
