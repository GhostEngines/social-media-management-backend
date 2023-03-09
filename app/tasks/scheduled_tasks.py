from datetime import datetime
from bson import ObjectId
from app.config.db import tasks
from app.youtube.youtube_post import content_post as youtube_post
from app.linkedin.linkedin_post import content_post as linkedin_post
from app.instagram.instagram_post import content_post as instagram_post
from app.facebook.facebook_post import content_post as facebook_post
from app.handlers.schemas import serializeDict, serializeList
from app.config.appConstants import appConstants
from os import remove
from fastapi.logger import logger as logging
from app.handlers.file_cloud_functions import delete_media

global_exclude = []


# EXECUTE EACH TASK

def execute_task(task):

    if task.get('type') == 'linkedin':
        linkedin_post(task)

    elif task.get('type') == 'youtube':
        youtube_post(task)

    elif task.get('type') == 'facebook':
        facebook_post(task)

    elif task.get('type') == 'instagram':
        instagram_post(task)

    remove(appConstants.local_filebase + task['file'])
    delete_media(str(task['file']))

    return serializeDict(tasks.find({'_id': ObjectId(task['_id'])}), global_exclude)


# GET THE LIST OF PENDING TASKS

def run_scheduled_tasks():
    logging.info('Running tasks check')
    date_now = str(datetime.utcnow()).split('.')[0]
    tasks_list = tasks.find({"$and": 
        [
            {'scheduled': {'$lte': datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")}},
            {'is_active': True},
            {'completed': False}
        ]
        })
    
    tasks_list = serializeList(tasks_list, global_exclude)

    logging.info(tasks_list)

    if tasks_list is not None:
        for task in tasks_list:
            try:
                execute_task(task)
            except Exception as e:
                logging.info('An error occurred {}'.format(e))

    return
