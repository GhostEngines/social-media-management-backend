from app.authenticate.services import Hash
from pytz import all_timezones
from app.config.appConstants import appConstants
from app.handlers.schemas import serializeDict
from datetime import datetime
from bson import ObjectId
from app.config.db import user_collection, accounts_collection
from app.tasks.db_task import delete_incomplete_tasks
from fastapi.logger import logger as logging

global_exclude = ['password']

# CREATE NEW USER

def create_user_db(user_details):

    if 'password' not in user_details or user_details['password'] == '':
        return {'status': 'Empty password'}

    if 'email' not in user_details or user_details['email'] == '':
        return {'status': 'Empty email'}

    if 'timezone' not in user_details or user_details['timezone'] not in all_timezones:
        user_details['timezone'] = appConstants.default_time_zone
    
    user_details['password'] = Hash.bcrypt(user_details['password'])
    date_now = str(datetime.utcnow()).split('.')[0]
    user_details['created_at'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    user_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    user_details['role'] = 'user'
    _id  = user_collection.insert_one(user_details)
    
    return serializeDict(user_collection.find_one({'_id': _id.inserted_id}), global_exclude)


# GET USER DETAILS

def get_user_db(user_id):
    return serializeDict(user_collection.find_one({'_id': ObjectId(user_id)}), global_exclude)


# UPDATE USER

def update_user_db(user, id):

    user_details = dict()
    
    for field in user:
        if user[field] != None and field != 'password' and field != 'timezone':
            user_details[field] = user[field]
        if field == 'password' and user[field] != None:
            user_details[field] = Hash.bcrypt(user[field])
        if field == 'timezone':
            if user[field] == '' or user[field] not in all_timezones:
                user_details[field] = appConstants.default_time_zone
            else:
                user_details[field] = user[field]
    
    date_now = str(datetime.utcnow()).split('.')[0]
    user_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") 
    user_collection.find_one_and_update({'_id': ObjectId(id)}, {'$set': user_details})

    return serializeDict(user_collection.find_one({"_id":ObjectId(id)}), global_exclude)    


# DELETE USER

def delete_user_db(id):
    logging.info(accounts_collection.delete_many({'owner': str(id)}))
    logging.info(delete_incomplete_tasks(id))
    logging.info(user_collection.find_one_and_delete({"_id":ObjectId(id)}))
    return {'status': 'Deleted'}

# PAYMENT METHODS

def update_subscription(id, type, subscription_id):

    # CREATE SUBSCRIPTION

    if type == 'create':
        logging.info('Subscription created for {}'.format(id))

        user = get_user_db(id)
        user_details = dict()
        for field in user:
            if field != '_id':
                user_details[field] = user[field]
    
        user_details['subscription_id'] = subscription_id
        
        date_now = str(datetime.utcnow()).split('.')[0]
        user_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")

        user_collection.find_one_and_update({'_id': ObjectId(id)}, {'$set': user_details})
        return serializeDict(user_collection.find_one({"_id":ObjectId(id)}), global_exclude)

    return {'status': 'success'}

# GET SUBSCRIPTION ID

def get_subscription_id(id):
    user = get_user_db(id)
    return user['subscription_id']