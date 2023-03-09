from fastapi import APIRouter, Depends
from app.user.models import LoginUser
from app.authenticate.services import get_current_user
from app.payments.services import create_subscription, fetch_subscription, cancel_user_subscription
from app.user.db_user import get_user_db

router = APIRouter(
     tags=['Payments'],
    prefix='/payments'     
)

# FETCH SUBSCRIPTIONS

@router.get('/')
def get_subscriptions(user: LoginUser = Depends(get_current_user)):
    id = user.user_id
    user_details = get_user_db(id)
    if 'subscription_id' in user_details:
        return {'subscription_id': user_details['subscription_id']}
    
    return fetch_subscription(id)

# SUBSCRIBE

@router.post('/')
def new_subscription(plan, user: LoginUser = Depends(get_current_user)):
    return create_subscription(user.user_id, plan)

# CANCEL SUBSCRIPTION

@router.delete('/')
def cancel_subscription(user: LoginUser = Depends(get_current_user)):
    print(user.user_id)
    return cancel_user_subscription(user.user_id)