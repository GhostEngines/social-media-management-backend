import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.youtube.services import get_and_store_creds
from app.config.appConstants import appConstants
from app.tasks.db_task import update_task
from fastapi.logger import logger as logging


RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
MAX_RETRIES = 3


# NAMESPACE CLASS

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# RESUMING UPLOAD

def resumable_upload(insert_request):
    try:
        logging.info("Uploading file...")
        status, response = insert_request.next_chunk()
        if response is not None:
            if 'id' in response:
                logging.info("Video id '%s' was successfully uploaded." % response['id'])
                return response['id']
            else:
                logging.exception(response)
                return {'error': "The upload failed with an unexpected response: %s" % response}
    except Exception as e:
        return {'error': 'An error occurred: %s' % e}


# INITIALIZING UPLOAD VIDEO

def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body=dict(
    snippet=dict(
        title=options.title,
        description=options.description,
        tags=tags,
        categoryId=options.category
    ),
    status=dict(
        privacyStatus=options.privacyStatus
    ))

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True
    ))

    try:
        logging.info(insert_request.to_json())
    except:
        logging.info(insert_request)

    resumable_upload(insert_request)



# CONTENT POST MAIN FUNCTION

def content_post(task):

    UPLOAD_DIRECTORY = appConstants.local_filebase

    file = UPLOAD_DIRECTORY + task['file']
    title = task['text'] if 'title' not in task else task['title']
    description = task['comments'] if 'description' not in task else task['description']
    category = 22 if 'category' not in task else task['category']
    keywords = 'surfing,Santa Cruz' if 'keywords' not in task else task['keywords']
    privacyStatus = 'public' if 'privacyStatus' not in task else task['privacyStatus']

    CRED_DIRECTORY = appConstants.local_cred_filebase
    
    cred_path = CRED_DIRECTORY + task['owner'] + '.pickle'
    args = Namespace(file=file, title=title, description=description, category=category, keywords=keywords, privacyStatus=privacyStatus)

    # token.pickle stores the user's credentials from previously successful logins
    error = None
    credentials = None

    if os.path.exists(cred_path):
        with open(cred_path, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            get_and_store_creds(cred_path)

    logging.info('Loading Credentials From Pickle File...')
    with open(cred_path, 'rb') as token:
        credentials = pickle.load(token)
        logging.info(credentials.to_json())

        youtube = build('youtube', 'v3', credentials=credentials)

        try:
            initialize_upload(youtube, args)
        
        except Exception as e:
            error = {'error' : "An HTTP error occurred:\n%s" % (e)}

    update_task(task['_id'], error)

    return {'status': 'success'}



# file = 'data/uploads/video.mp4'
# title = 'Summer vacation in California'
# description = 'Had fun surfing in Santa Cruz'
# category = 22
# keywords = 'surfing,Santa Cruz'
# privacyStatus = 'public'      
# user_data_path = 'data/creds/'
# args = Namespace(file=file, title=title, description=description, category=category, keywords=keywords, privacyStatus=privacyStatus)

# cred_path = 'data/creds/token.pickle'

# # get_and_store_creds(cred_path)
# content_post(args, cred_path)