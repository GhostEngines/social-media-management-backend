import razorpay
from app.config.appConstants import appConstants
from fastapi.logger import logger as logging
from app.user.db_user import get_subscription_id, update_subscription

# RAZORPAY SUBSCRIPTION ENDPOINTS
# REFERENCE : https://github.com/razorpay/razorpay-python/blob/master/documents/subscription.md


client = razorpay.Client(auth=(appConstants.payment_gateway_credentials['api_id'], appConstants.payment_gateway_credentials['api_secret']))
client.set_app_details({"title" : "smm", "version" : "1.0"})


# CREATE SUBSCRIPTION

def create_subscription(id, plan = 'Basic'):
    if plan == 'Basic':
        plan = appConstants.subscription_options['basic']
    elif plan == 'Pro':
        plan = appConstants.subscription_options['pro']
    else:
        plan = appConstants.subscription_options['basic']
    
    resp = client.subscription.create({
            "plan_id": plan,
            "total_count": 1,
            "quantity": 1,
            "customer_notify": 1,
            "notes": {
                "notes_key_1": "Tea, Earl Grey, Hot",
                "notes_key_2": "Tea, Earl Grey… decaf."
            },
            "notify_info": {
                "notify_phone": 7305528208,
                "notify_email": "ghostengines.io@gmail.com"
            }
    })

    logging.info(resp)
    subscription_id = resp['id']
    type = 'create'

    update_subscription(id, type, subscription_id)
    payment_url = resp['short_url']

    return {'status': 'success', 'payment_url': payment_url}


# CANCEL SUBSCRIPTION

def cancel_user_subscription(id):
    subscription_id = get_subscription_id(id)
    resp = client.subscription.cancel(subscription_id)

    return resp


# FETCH ALL SUBSCRIPTIONS OF USER

def fetch_subscription(id):
    subscription_id = get_subscription_id(id)
    resp = client.invoice.all({'subscription_id':subscription_id})

    return resp


# PAYMENT VERIFICATION
# REFERENCE: https://razorpay.com/docs/api/payments/subscriptions/

def verify_payment(order_id, payment_id, signature):
    resp = client.utility.verify_payment_signature({
    'razorpay_order_id': order_id,
    'razorpay_payment_id': payment_id,
    'razorpay_signature': signature
    })

    return resp
