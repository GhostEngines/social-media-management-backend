from app.config.db import accounts_collection
from app.config.appConstants import appConstants
from app.tasks.db_task import update_task
from requests import post
from json import loads
from app.handlers.schemas import serializeDict
from app.handlers.file_cloud_functions import upload_media
from os.path import getsize
from fastapi.logger import logger as logging


def create_post(type, file_path, caption, access_token, page_id):

    # REFERENCES: https://developers.facebook.com/docs/pages/publishing

    api_version = '14.0'

    resp = None

    if type == 'image':

        # curl -i -X POST "https://graph.facebook.com/{page-id}/photos
        # ?url={path-to-photo}
        # &access_token={page-access-token}"

        url = 'https://graph.facebook.com/{}/photos'.format(page_id)

        params = {
            'url': file_path,
            'access_token': access_token,
        }

        headers = {
            'Content-Type': 'application/json'
        }

        resp = post(url, params=params, headers= headers)

        logging.info(resp.content)

        return {'post_id': loads(resp.content)['post_id'], 'status': loads(resp.content)}


    elif type == 'video':
        
        filesize = getsize(file_path)

        # SESSION START

        # curl -X POST \
        #   "https://graph-video.facebook.com/v14.0/1755847768034402/videos" \
        #   -F "upload_phase=start" \
        #   -F "access_token=EAADI..." \
        #   -F "file_size=22420886"

        url = 'https://graph-video.facebook.com/v{}/{}/videos'.format(api_version, page_id)

        params = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': filesize
        }

        resp = post(url, params=params)

        logging.info(loads(resp.content))

        resp = loads(resp.content)

        upload_session_id = resp['upload_session_id']
        video_id = resp['video_id']


        # FIRST CHUNK

        # curl -X POST \
        #   "https://graph-video.facebook.com/v14.0/1755847768034402/videos"  \
        #   -F "upload_phase=transfer" \
        #   -F "upload_session_id=2918040901584241" \
        #   -F "access_token=EAADI..." \
        #   -F "start_offset=0" \
        #   -F "video_file_chunk=@/Users/...xaa"


        url = 'https://graph-video.facebook.com/v{}/{}/videos'.format(api_version, page_id)


        multipart_form_data = {
            'video_file_chunk': (str(file_path.split('/')[-1]), open(file_path, 'rb')),
        }

        data = {
            'start_offset': 0,
            'upload_session_id': upload_session_id,
            'upload_phase': 'transfer',
            'access_token': access_token    
        }

        resp = post(url, files=multipart_form_data, data=data)

        logging.info(loads(resp.content))


        # END SESSION

        # POST /v14.0/{page-id}/videos
        #   ?upload_phase=finish
        #   &access_token={access-token}
        #   &upload_session_id={upload-session-id}

        url = 'https://graph-video.facebook.com/v{}/{}/videos'.format(api_version, page_id)

        params = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id
        }

        resp = post(url, params=params)

        logging.info(loads(resp.content))
      
        return {'video_id': video_id, 'status': loads(resp.content)}


    return {'status': 'Type not supported'}


# MAIN CONTENT POST FUNCTION

def content_post(task):

    f_name = task['file']
    caption = task['text']
    comments = task['comments']
    owner = task['owner']

    UPLOAD_DIRECTORY = appConstants.local_filebase

    path = UPLOAD_DIRECTORY + f_name

    account_details = serializeDict(accounts_collection.find_one({"$and": [{"owner": owner}, {"type": 'facebook'}]}), [])

    access_token = account_details['page_access_token']

    page_id= account_details['page_id']

    extension = f_name.split('.')[-1]

    if extension == 'jpeg':
        media_type = 'image'
        file_path = task['file_url'] #upload_media(path)

    elif extension == 'mp4':
        media_type = 'video'
        file_path = path

    post_details = create_post(media_type, file_path, caption, access_token, page_id)

    update_task(task['_id'], post_details)
    
    return {'status': 'success'}
