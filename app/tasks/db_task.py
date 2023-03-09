from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from app.config.db import tasks, user_collection
from app.handlers.schemas import serializeDict, serializeList
from os.path import splitext, join
from app.config.appConstants import appConstants
from app.handlers.file_cloud_functions import delete_media, upload_media
from app.handlers.media_handler import media_handler
from os import remove
from pytz import timezone, utc
from fastapi.logger import logger as logging
from fastapi import status


# REFERENCES:
# https://stackoverflow.com/questions/79797/how-to-convert-local-time-string-to-utc


# SHOW ALL TASKS
async def get_tasks(id, type = '', completed= ''):

    if not id:
        return {'status': 'Empty id'}

    if completed == '':
        return serializeList(tasks.find({"$and": [{"owner": id},{"type": type}]}), [])
    
    elif completed == True:
        return serializeList(tasks.find({"$and": [{"owner": id},{"type": type},{"is_active": False}, {"completed": True}]}), [])

    elif completed == False:
        return serializeList(tasks.find({"$and": [{"owner": id},{"type": type},{"is_active": True}, {"completed": False}]}), [])

    else:
        return {'error': 'Valid input expected'}

# ADD NEW TASK

async def add_task(id, item, file, type = ''):

    extension = splitext(file.filename)[-1]

    if extension[1:] not in appConstants.allowed_extensions:
        return {'error': 'File extension not allowed'}

    f_name = str(uuid4()) + extension
    contents = await file.read()

    # if getsize(contents) == 0:
    #     return {'error': 'Upload non empty file'}
    
    UPLOAD_DIRECTORY = appConstants.local_filebase
 
    with open(join(UPLOAD_DIRECTORY, f_name), "wb") as fp:
        fp.write(contents)
    
    status, error = media_handler(type, UPLOAD_DIRECTORY + f_name, extension[1:])

    if status == 'Abort':
        remove(UPLOAD_DIRECTORY + f_name)
        logging.info(error)
        return {'error': error}

    status, attribute = upload_media(UPLOAD_DIRECTORY + f_name)
    
    if status == 'error':
        file_url = ''
        logging.info(status)
    
    else:
        file_url = attribute

    user_details = serializeDict(user_collection.find_one({'_id': ObjectId(id)}), [])

    tasks_details = dict()
    local = timezone(user_details['timezone'])
    date_now = str(datetime.utcnow()).split('.')[0]
    scheduled = str(item.scheduled).split('.')[0]
    utc_created_at = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    tasks_details['created_at'] = utc_created_at
    native_scheduled_at = datetime.strptime(scheduled, "%Y-%m-%d %H:%M:%S")
    utc_scheduled_at = local.localize(native_scheduled_at, is_dst=None).astimezone(utc)
    tasks_details['scheduled'] = utc_scheduled_at
    tasks_details['type'] = type
    tasks_details['text'] =  item.text
    tasks_details['comments'] = item.comments
    tasks_details['owner'] = id
    tasks_details['file'] = str(f_name)
    tasks_details['is_active'] = True
    tasks_details['completed'] = False
    tasks_details['description'] = item.description
    tasks_details['category'] = item.category
    tasks_details['file_url'] = file_url

    _id  = tasks.insert_one(tasks_details)

    return serializeDict(tasks.find_one({'_id': _id.inserted_id}), [])


# UPDATE TASK

def update_task(id, details = None):

    if not tasks.find_one({'_id': ObjectId(id)}):
        return {'status': 'Task doesn\'t exists'}

    task_details = dict()
    
    date_now = str(datetime.utcnow()).split('.')[0]
    task_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    task_details['is_active'] = False
    task_details['completed'] = True

    if details is not None:
        for key in details:
            task_details[key] = details[key]

    tasks.find_one_and_update({"_id":ObjectId(id)},{"$set":task_details})

    return serializeDict(tasks.find_one({"_id":ObjectId(id)}), [])


# DELETE TASK

def delete_tasks(id, tasks_list):

    errors = []

    logging.info(tasks_list)
    
    for task in tasks_list:
        try:
            logging.info(task)
            task_ = tasks.find_one({"$and": [{"owner": id},{"_id": ObjectId(task)}]})
            logging.info(task_)
            
            remove(appConstants.local_filebase + task_['file'])
            logging.info('Removed from local storage')
            
            status, error = delete_media(str(task_['file']))
            logging.info(status, error)

            if status != 'error':
                tasks.find_one_and_delete({"$and": [{"owner": id},{"_id": ObjectId(task)}]})
            else:
                tasks.find_one_and_delete({"$and": [{"owner": id},{"_id": ObjectId(task)}]})
                errors.append({'error': error, 'id': task})
        
        except Exception as e:
            logging.info('An error occurred {}'.format(e))
            errors.append({'error': e, 'id': task})

    if len(errors) == 0:
        logging.info({'status': 'Deleted'})
        return {'status': 'Deleted'}

    else:
        logging.info(errors)
        return {'errors': errors}


# EXECUTE TASKS NOW

# def execute_tasks_now(id, tasks):
    
#     arr = []
#     for task in tasks:
        
#         try:
#             logging.info(task)
#             task_ = tasks.find_one({"$and": [{"owner": id},{"_id": ObjectId(task)}]})
#             logging.info(task_)

#             execute_task(task_)
            
#         except Exception as e:
#             logging.info('An error occurred {}'.format(e))
#             arr.append(task)

#     if len(arr) == 0:
#         return {'status': 'success'}
#     else:
#         return {'Following not modified': arr}


# DELETE ALL INCOMPLETE TASKS OF USER

def delete_incomplete_tasks(id):
    return tasks.delete_many({"$and": [{"owner": id},{"completed": False}]})    
