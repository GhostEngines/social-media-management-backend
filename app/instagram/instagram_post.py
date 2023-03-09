
# Instagram accounts are limited to 25 API-published posts within a 24 hour moving period. 
# Carousels count as a single post. 

from time import time
from app.config.db import accounts_collection
from app.config.appConstants import appConstants
from app.tasks.db_task import update_task
from requests import post, get
from json import loads
from app.handlers.schemas import serializeDict
from fastapi.logger import logger as logging


def create_post(type, media_url, caption, access_token, ig_user_id):

    # REFERENCES: https://developers.facebook.com/docs/instagram-api/reference/ig-user/media

    # location_id --> Page ID of the location you want to post the photo to.
    # ig_user_id --> User ID of the Instagram account you want to post the photo to.


    if type == 'image':
        # POST https://graph.facebook.com/{api-version}/{ig-user-id}/media
        # ?image_url={image-url}
        # &is_carousel_item={is-carousel-item}
        # &caption={caption}
        # &location_id={location-id}
        # &user_tags={user-tags}
        # &access_token={access-token}
        
        # media_url = 'https://img.freepik.com/free-psd/social-media-instagram-post-template_47618-73.jpg?w=2000'
        
        params = {
            'image_url': media_url,
            'caption': caption,
            # 'is_carousel_item': 'false',
            'access_token': access_token,
            # 'location_id': location_id
        }

    elif type == 'video':
        # POST https://graph.facebook.com/{api-version}/{ig-user-id}/media
        # ?media_type=VIDEO
        # &video_url={video-url}
        # &is_carousel_item={is-carousel-item}
        # &caption={caption}
        # &location_id={location-id}
        # &thumb_offset={thumb-offset}
        # &access_token={access-token}     
        
        # media_url = 'https://jinnss-assets.s3.ap-south-1.amazonaws.com/Walking+in+the+nature+park.mp4'    

        sample_req = 'https://graph.facebook.com/v14.0/{}/media'.format(ig_user_id)
        params = {
            'access_token': access_token,
        }
        logging.info(get(sample_req, params=params).content)

        params = {
            'media_type': 'VIDEO',
            'video_url': media_url,
            'caption': caption,
            # 'is_carousel_item': 'false',
            'access_token': access_token,
            # 'location_id': location_id
        }

    else:
        return {'status': 'Error'}

    headers = {
        'Content-Type': 'application/json'
    }

    api_version = '14.0'

    url = 'https://graph.facebook.com/v' + str(api_version) + '/' + str(ig_user_id) + '/media'

    resp = post(url, params=params, headers= headers)

    logging.info(resp.url)

    logging.info(resp.content)

    if resp.status_code == 200 or resp.status_code == 201:
        resp = loads(resp.content)

        container_id = resp['id']

    else:
        container_id = ''

    # PUBLISH MEDIA ITEMS

    # REFERENCE: https://developers.facebook.com/docs/instagram-api/reference/ig-user/media_publish

    # POST https://graph.facebook.com/{api-version}/{ig-user-id}/media_publish
    # ?creation_id={creation-id}
    # &access_token={access-token}

    # container_id = '17962812652738661'

    url = 'https://graph.facebook.com/v' + str(api_version) + '/' + str(ig_user_id) + '/media_publish'

    params = {
        'creation_id': container_id,
        'access_token': access_token
    }
    
    resp = post(url, params=params, headers=headers)

    if resp.status_code == 200 or resp.status_code == 201:
        resp = loads(resp.content)

        publish_id = resp['id']
    
    else:
        publish_id = ''

    logging.info(resp)


    # CHECK STATUS OF PUBLISH

    # GET https://graph.facebook.com/{ig-container-id}
    # ?fields={fields}
    # &access_token={access-token}    

    url = 'https://graph.facebook.com/' + str(container_id)

    params = {
        'fields': 'status_code',
        'access_token': access_token
    }

    resp = get(url, params=params)

    if resp.status_code == 200 or resp.status_code == 201:
        resp = loads(resp.content)

        status_code = resp['status_code']

    else:
        status_code = ''
    
    logging.info(resp)

    update_stats = dict()

    update_stats['container_id'] = container_id
    update_stats['publish_id'] = publish_id
    update_stats['status_code'] = status_code
    
    return update_stats


# MAIN CONTENT POST FUNCTION

def content_post(task):

    logging.info(task)

    f_name = task['file']
    caption = task['text']
    comments = task['comments']
    owner = task['owner']

    UPLOAD_DIRECTORY = appConstants.local_filebase

    path = UPLOAD_DIRECTORY + f_name

    logging.info(path)

    account_details = serializeDict(accounts_collection.find_one({"$and": [{"owner": owner}, {"type": 'instagram'}]}), [])
    # location_id = account_details['org_location_id']
    # access_token = account_details['page_access_token']
    access_token = account_details['access_token']

    ig_user_id= account_details['user_id']
    # ig_user_id= '53653709259' # account_details['page_id']

    logging.info(account_details)

    extension = f_name.split('.')[-1]

    logging.info(extension)

    if extension == 'jpeg' or 'jpg':
        media_type = 'image'
    elif extension == 'mp4':
        media_type = 'video'

    media_url = task['file_url'] # upload_media(path)

    post_details = create_post(media_type, media_url, caption, access_token, ig_user_id)

    update_task(task['_id'], post_details)
    
    return