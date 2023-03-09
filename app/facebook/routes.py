import logging
from fastapi import APIRouter, File, Request, Depends, BackgroundTasks, UploadFile, status
from pyparsing import Optional
from app.account.models import InsertIndividualAccount, UpdateIndividualAccount
from app.tasks.models import ItemForm
from app.user.models import LoginUser
from app.account.db_account import add_account, delete_account, get_accounts, update_account
from app.tasks.db_task import add_task, delete_tasks, get_tasks
from app.authenticate.services import get_current_user
from app.facebook.services import get_access_token, get_temp_token


global_exclude = ['refresh_token', 'access_token', 'page_access_token']


router = APIRouter(
     tags=['Facebook'],
    prefix='/facebook'     
)

TYPE = 'facebook'


# GET EXISTING ACCOUNT

@router.get('/')
def get_account(user: LoginUser = Depends(get_current_user)):

    user_id = str(user.user_id)
    logging.info(user_id)

    if not id:
        return {'status': 'Empty id'}
    
    return get_accounts(user_id, global_exclude, type=TYPE)



# CREATE A NEW ACCOUNT

@router.post('/')
def add(account :InsertIndividualAccount, user: LoginUser = Depends(get_current_user)):
    
    user_id = str(user.user_id)
    account = dict(account)

    if not user_id:
        return {'status': 'Empty user_id'}

    try:
        inserted_id, account_details = add_account(user_id, account, global_exclude, type=TYPE)
        
        if account_details == 'Account already exists':
            return {'status': 'Account already exists'}
        
        result = dict()
        result['auth_url'] = get_temp_token(str(inserted_id))
        result['account_details'] = account_details        
        return result

    except:
        return {'status': 'Error'}



# UPDATE EXISTING ACCOUNT

@router.put('/')
def update(account :UpdateIndividualAccount, user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}

    return update_account(id, account, global_exclude)


# DELETE EXISTING ACCOUNT

@router.delete('/')
async def delete(user: LoginUser = Depends(get_current_user)):
    
    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}

    delete_account(id)
    
    return {'status': 'Account deleted'} 


# GET ALL TASKS

@router.get('/tasks')
async def get_all_tasks(completed: bool ,user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}

    return await get_tasks(id, type=TYPE, completed = completed)


# UPLOAD PHOTOS

@router.post('/tasks', status_code=status.HTTP_201_CREATED)
async def upload_file(
                    item: ItemForm = Depends(ItemForm.as_form),
                    file: UploadFile = File(...),
                    user: LoginUser = Depends(get_current_user)):
    
    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}

    return await add_task(id, item, file, type=TYPE)  


# DELETE TASKS

@router.delete('/tasks', status_code=status.HTTP_200_OK)
def delete_multiple_tasks(
    tasks: list[str],
    user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)

    if not id:
        return {'status': 'Empty id'}
    
    return delete_tasks(id, tasks)


# EXECUTE TASKS IMMEDIATELY

# @router.patch('/tasks', status_code=status.HTTP_201_CREATED)
# def execute_tasks(
#     tasks: list[str],
#     user: LoginUser = Depends(get_current_user)):

#     id = str(user.user_id)

#     if not id:
#         return {'status': 'Empty id'}
    
#     return execute_tasks_now(id, tasks)


# GET ACCESS TOKEN

@router.get('/{path:path}', include_in_schema = False)
async def access(path, request: Request, background_tasks:BackgroundTasks):
    
        background_tasks.add_task(get_access_token, request)

        return {'status': 'added to tasks'}
    
