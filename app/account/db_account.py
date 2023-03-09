from datetime import datetime
from bson import ObjectId
from app.config.db import accounts_collection
from app.handlers.schemas import serializeDict, serializeList

# ADD NEW ACCOUNT IN DB

def add_account(user_id, account, global_exclude, type = ''):
    
    if accounts_collection.find_one({"$and": [{"owner": user_id},{"type": type}]}) is not None:
        return ('status', 'Account already exists')

    if account['org_id'] != None and accounts_collection.find_one({'org_id': account['org_id']}) is not None:
        return ('status', 'Account already exists')

    account_details = dict()
    
    date_now = str(datetime.utcnow()).split('.')[0]
    account_details['created_at'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    account_details['type'] = type
    account_details['owner'] = user_id
    account_details['org_id'] = account['org_id']
    
    _id  = accounts_collection.insert_one(account_details)

    account_details = {}
    inserted_id = _id.inserted_id

    account_details = serializeDict(accounts_collection.find_one({'_id': ObjectId(_id.inserted_id)}), global_exclude)

    return (inserted_id, account_details)


# UPDATE ACCOUNT IN DB

def update_account(user_id, account, global_exclude, type = ''):

    account = dict(account)

    if not accounts_collection.find_one({"$and": [{"owner": user_id},{"type": type}]}):
        return {'status': 'Account doesn\'t exists'}

    account_details = dict()
    
    for field in account:
        if account[field] != None:
            account_details[field] = account[field]
    
    date_now = str(datetime.utcnow()).split('.')[0]
    account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") 
    accounts_collection.find_one_and_update({"_id":ObjectId(id)},{"$set":account_details})
    account_details = serializeDict(accounts_collection.find_one({"_id":ObjectId(id)}), global_exclude)

    return account_details


# GET ACCOUNT

def get_accounts(user_id, global_exclude, type = ''):
    if not user_id:
        return {'status': 'Empty user_id'}
    
    account = accounts_collection.find_one({"$and": [{"owner": user_id}, {"type": type}]})
    
    if not account:
        return {'status': 'couldn\'t fetch'}

    return serializeDict(account, global_exclude)


# DELETE ACCOUNT

def delete_account(user_id, type = ''):
    
    return accounts_collection.find_one_and_delete({"$and": [{"owner": user_id},{"type": type}]})

