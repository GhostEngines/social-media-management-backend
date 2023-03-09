from fastapi import APIRouter, File, Depends, UploadFile, status
from app.account.models import InsertIndividualAccount, UpdateIndividualAccount
from app.tasks.models import ItemForm
from app.user.models import LoginUser
from app.account.db_account import add_account, delete_account, get_accounts, update_account
from app.tasks.db_task import add_task, delete_tasks, get_tasks
from app.authenticate.services import get_current_user
from app.youtube.services import get_and_store_creds


global_exclude = ['refresh_token', 'access_token']


router = APIRouter(
     tags=['Youtube'],
    prefix='/youtube'     
)


TYPE = 'youtube'


# GET EXISTING ACCOUNT

@router.get('/')
def get_account(user: LoginUser = Depends(get_current_user)):

    user_id = str(user.user_id)
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
        
        get_and_store_creds(str(user_id))

        result = dict()
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

    delete_account(id, type=TYPE)
    
    return {'status': 'Account deleted'} 


# GET ALL TASKS

@router.get('/tasks')
async def get_all_tasks(completed: bool ,user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}

    return await get_tasks(id, type=TYPE, completed = completed)


# DELETE TASKS

@router.delete('/tasks', status_code=status.HTTP_200_OK)
def delete_multiple_tasks(
    tasks: list[str],
    user: LoginUser = Depends(get_current_user)):

    id = str(user.user_id)
    if not id:
        return {'status': 'Empty id'}
    
    return delete_tasks(id, tasks)


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
