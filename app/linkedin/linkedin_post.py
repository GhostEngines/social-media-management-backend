from bson import ObjectId
from app.handlers.schemas import serializeDict
from app.config.db import accounts_collection
from app.config.appConstants import appConstants
from json import loads, dumps
from requests import post, get, put
from app.tasks.db_task import update_task
from fastapi.logger import logger as logging


# UPLOAD MEDIA TO LINKEDIN

def upload_media(org_id, access_token, path):

    # REFERENCE:
    # https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/vector-asset-api?tabs=http


    # REGISTER AN UPLOAD

    extension = path.split('.')[-1]

    if extension == 'jpg':
        media_type = 'image/jpeg'
    elif extension == 'png':
        media_type = 'image/png'
    elif extension == 'gif':
        media_type = 'image/gif'
    elif extension == 'mp4':
        media_type = 'video/mp4'


    base_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'

    header = {
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

    data = {
                "registerUploadRequest":{
                    "owner":org_id,
                    "recipes":[
                        "urn:li:digitalmediaRecipe:feedshare-{}".format(media_type.split('/')[0])
                    ],
                    "serviceRelationships":[
                        {
                            "identifier":"urn:li:userGeneratedContent",
                            "relationshipType":"OWNER"
                        }
                    ],
                    
                }
            }


    resp = post(base_url, data=dumps(data), headers=header)

    if resp.status_code == 200:
        resp = loads(resp.content)
        upload_url = resp['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = resp['value']['asset']     

    else:
        return resp.content
    

    # UPLOAD IMAGE

    header = {
        'Authorization': 'Bearer {}'.format(access_token),
        # 'Content-Type': 'image/jpeg',
        'Content-Type': media_type
        }

    if 'http' in path:

        rsrc = get(path)
        resp = put(upload_url, headers=header, data=rsrc)#open(path,'rb'))
    
    else:

        resp = put(upload_url, headers=header, data= open(path,'rb'))

    # CHECK STATUS OF UPLOAD

    check_url = 'https://api.linkedin.com/v2/assets/{}'.format(asset.split(':')[-1])

    header = {
                'Authorization': 'Bearer {}'.format(access_token),
             }

    resp = get(check_url, headers=header)

    if resp.status_code == 200 or resp.status_code == 201:
        resp = loads(resp.content)

        return resp['id']
    
    return {'status': 'failed'}



# CREATE A LINKEDIN POST

def create_post(org_id, access_token, title, media_type, comments, media_id):

    logging.info('Creating linkedin post')

    contents = {
                    "author": org_id,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                        "media": [
                            {
                            "media": "urn:li:digitalmediaAsset:" + str(media_id),
                            "status": "READY",
                            "title": {
                                "attributes": [],
                                "text": title
                            }
                            }
                        ],
                        "shareCommentary": {
                            "attributes": [],
                            "text": comments
                        },
                                "shareMediaCategory": media_type
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
    

    # POST https://api.linkedin.com/v2/posts

    base_url = 'https://api.linkedin.com/v2/ugcPosts'

    headers = {
            "Content-Type": "application/json", 
            'Authorization': 'Bearer {}'.format(access_token),
            'X-Restli-Protocol-Version': '2.0.0'
            }

    resp = post(base_url, data=dumps(contents), headers=headers)

    logging.info(loads(resp.content))

    resp = loads(resp.content)

    return resp



# TASK SCHEDULER LINKEDIN POST

def content_post(task):

    f_name = task['file']
    title = task['text']
    comments = task['comments']
    owner = task['owner']
    if 'http' in f_name:
        path = f_name
    
    else:
        UPLOAD_DIRECTORY = appConstants.local_filebase

        path = UPLOAD_DIRECTORY + f_name

    account_details = serializeDict(accounts_collection.find_one({"$and": [{"owner": owner}, {"type": 'linkedin'}]}), [])
    
    org_id = account_details['org_id']
    access_token = account_details['access_token']

    post_id = upload_media(org_id, access_token, path)

    extension = f_name.split('.')[-1]

    if extension == 'jpg' or extension == 'png' or extension == 'gif':
        media_type = 'IMAGE'
    elif extension == 'mp4':
        media_type = 'VIDEO'

    create_post(org_id, access_token, title, media_type, comments, post_id)

    update_task(task['_id'], None)

    return {'status': 'success'}

# task = dict()

# task['file'] = 'https://jinnss-assets.s3.ap-south-1.amazonaws.com/Leadsmagnet.png'
# task['comments'] = ''
# task['text'] = 'Leads Magnet'
# task['owner'] = '62a9fc92b81806a6c1162258'
# task['org_id'] = 'urn:li:organization:13266326'

# content_post(task)