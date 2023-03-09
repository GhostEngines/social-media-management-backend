# FACEBOOK REGISTER FUNCTIONS

from urllib.parse import urlencode
from requests import post, get
from json import loads
from app.config.appConstants import appConstants
from datetime import datetime
from bson import ObjectId
from app.config.db import accounts_collection
from requests.utils import unquote
from fastapi.logger import logger as logging


# DECODE THE CODE AND GET THE ACCESS TOKEN, REFRESH TOKEN, USER ID AND STORE IN DB 

def get_access_token(request):

    # GET THE STATE AND CODE FROM THE REQUEST

    logging.info(request.query_params)

    try:
        query_url = str(request.query_params)
        query_url = str(unquote(query_url)).split('&')
        for elem in query_url:
            if 'state' in elem:
                lis = elem.split('=')
                for i in range(len(lis)):
                    if 'state' in lis[i]:
                        state = lis[1+i].strip().replace('\'', '').replace(',', '')
        logging.info('state: ' , state)
        code = request.query_params.get('code')
        logging.info(code)

    except:
        return {'status': 'Error'}

    state = str(state)
    
    client_id = appConstants.facebook['FACEBOOK_CLIENT_ID']
    client_secret = appConstants.facebook['FACEBOOK_CLIENT_SECRET']

    # grant_type = 'authorization_code'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    access_token_url = 'https://graph.facebook.com/v14.0/oauth/access_token'

    redirect_uri = appConstants.facebook['FACEBOOK_REDIRECT_URL']

    params = {
        # 'grant_type': grant_type,
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }

    resp = post(access_token_url, params=params, headers=headers, timeout=10)

    logging.info(resp.content)

    if resp.status_code == 200:
        resp = loads(resp.text)

        logging.info(resp)

        if 'access_token' in resp:

            if 'access_token' in resp:
                access_token = resp['access_token']

    else:
        access_token = ''


    # EXCHANGE FOR LONG TERM ACCESS TOKEN

    logging.info('EXCHANGE FOR LONG TERM ACCESS TOKEN...')

    grant_type = 'fb_exchange_token'


    access_token_url = 'https://graph.facebook.com/v14.0/oauth/access_token'

    params = {
        'grant_type': grant_type,
        # 'redirect_uri': redirect_uri,
        'fb_exchange_token': access_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    resp = post(access_token_url, params=params, headers=headers, timeout=10)

    logging.info(resp.content)

    if resp.status_code == 200 or resp.status_code == 201:
        resp = loads(resp.text)
        logging.info(resp)
        if 'access_token' in resp:
            access_token = resp['access_token']
            logging.info(access_token)

    else:
        access_token = ''


    
    logging.info('GET THE USER ID AND NAME FROM THE ACCESS TOKEN...')

    url = 'https://graph.facebook.com/v14.0/me'

    headers = {
        'Content-Type': 'application/json'
    }

    params = {
        'fields': 'accounts',
        'access_token': access_token
    }

    resp = get(url, headers=headers, params=params)

    logging.info(resp.content)

    if resp.status_code == 200 or resp.status_code == 201:

        resp = loads(resp.content)

        logging.info(resp)

        if 'accounts' in resp:
            page_access_token = resp['accounts']['data'][0]['access_token']
            page_id = resp['accounts']['data'][0]['id']
            page_name = resp['accounts']['data'][0]['name']

    else:
        page_access_token = ''
        page_id = ''
        page_name = ''


    account_details = dict()
    account_details['page_id'] = page_id
    account_details['account_name'] = page_name
    account_details['access_token'] = access_token
    account_details['page_access_token'] = page_access_token
    date_now = str(datetime.utcnow()).split('.')[0]
    account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
    logging.info(account_details)

    accounts_collection.find_one_and_update({"_id":ObjectId(state)},{"$set":account_details})

    return {'status': 'success'}



# GETS TEMPORARY ACCESS TOKEN

def get_temp_token(state):

    # https://levelup.gitconnected.com/automating-instagram-posts-with-python-and-instagram-graph-api-374f084b9f2b

    client_id = appConstants.facebook['FACEBOOK_CLIENT_ID']

    logging.info(client_id)

    auth_url = 'https://www.facebook.com/v14.0/dialog/oauth'

    response_type = 'code'

    redirect_uri = appConstants.facebook['FACEBOOK_REDIRECT_URL']

    scopes = [
            'business_management',
            'pages_show_list',
            'pages_manage_posts',
            'public_profile',
            'pages_read_engagement',
            'ads_management',
            'publish_to_groups',
            'publish_video',
            'read_insights',
            'page_events',
            'pages_manage_metadata',
            # 'user_location'
            ]

    fin_scope = ''

    for scope in scopes:
        fin_scope = fin_scope + str(scope) + ','

    scope = fin_scope[:-1]

    params = {
        'response_type': response_type,
        'redirect_uri': redirect_uri,
        'state': state,
        'client_id': client_id,
        'scope': scope
    }

    # oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    
    # authorization_url, _ = oauth.authorization_url(auth_url, params=params)

    authorization_url = auth_url + '?' + urlencode(params)
    
    return str(authorization_url) #+ '&state={}'.format(state)
