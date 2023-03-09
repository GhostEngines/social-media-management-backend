from fastapi import APIRouter, Depends
from app.user.db_user import create_user_db, get_user_db, delete_user_db, update_user_db
from app.user.models import InsertUser, UpdateUser, LoginUser
from app.authenticate.services import get_current_user
from pytz import all_timezones
from fastapi.logger import logger as logging

router = APIRouter(
    tags=["User"],
    prefix='/user'
)

global_exclude = ['password']


# # GET ALL FILES
# @router.get('/')
# def get_folders():
#     list_ = listdir('/')
#     return {'folders': list_}


# NEW USER REGISTRATION

@router.post('/')
async def create_user(user: InsertUser):
    
    if not user:
        return {'status': 'Empty user'}
    
    user_details = dict(user)

    return create_user_db(user_details)


# GET ME
@router.get('/me')
def get_me(user: LoginUser = Depends(get_current_user)):

    return get_user_db(user.user_id)

# UPDATE EXISTING USER

@router.put('/me')
async def update_user(user: UpdateUser, _: LoginUser = Depends(get_current_user)):

    id = str(_.user_id)

    logging.info(id)

    if not id:
        return {'status': 'Empty user_id'}

    user = dict(user)

    return update_user_db(user, id)


# DELETE EXISTING USER

@router.delete('/me')
async def delete_user(user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)

    logging.info(id)

    if not id:
        return {'status': 'Empty user_id'}

    return delete_user_db(id)


# GET ALL TIMEZONES

@router.get('/timezones')
def get_timezones():
    return all_timezones
