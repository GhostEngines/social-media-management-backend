from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from app.config.appConstants import appConstants

pwd_context = CryptContext(schemes=['bcrypt'])

class Hash():
    def bcrypt(password: str):
        return pwd_context.hash(password)
    
    def verify(hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_email: str
    user_id: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=appConstants.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, appConstants.secret_key, algorithm=appConstants.hash_algorithm)
    return encoded_jwt


def verify_token(token : str, credentials_exception):
    try:
        payload = jwt.decode(token, appConstants.secret_key, algorithms=[appConstants.hash_algorithm])
        user_email: str = payload.get("username")
        if user_email is None:
            raise credentials_exception
        user_id: str = payload.get("user_id")
        token_data = TokenData(user_email = user_email, user_id = user_id)
    except JWTError:
        raise credentials_exception
    return token_data
