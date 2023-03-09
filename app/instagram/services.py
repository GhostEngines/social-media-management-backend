# INSTAGRAM REGISTER FUNCTIONS

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

    print(request.query_params)

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
    
    client_id = appConstants.instagram['INSTAGRAM_CLIENT_ID']
    client_secret = appConstants.instagram['INSTAGRAM_CLIENT_SECRET']

    # grant_type = 'authorization_code'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    access_token_url = 'https://graph.facebook.com/v14.0/oauth/access_token'

    redirect_uri = appConstants.instagram['INSTAGRAM_REDIRECT_URL']

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
        if 'access_token' in resp:
            access_token = resp['access_token']
            logging.info(access_token)

    else:
        access_token = ''


    # account_details = dict()
    # account_details['access_token'] = access_token
    # date_now = str(datetime.utcnow()).split('.')[0]
    # account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") 
    # accounts_collection.find_one_and_update({"_id":ObjectId(state)},{"$set":account_details})



    # # GET THE USER ID AND NAME FROM THE ACCESS TOKEN

    # ig_account = serializeDict(accounts_collection.find_one({"_id":ObjectId(state)}))

    # # curl -i -X GET \
    # # "https://graph.facebook.com/v10.0/{facebook_page_id}?fields=instagram_business_account&access_token={access-token}"

    # facebook_page_id = ig_account['org_id']
    # access_token = ig_account['access_token']
    
    # url = "https://graph.facebook.com/v10.0/{}".format(facebook_page_id)

    # headers = {
    #     'Content-Type': 'application/json'
    # }

    # params = {
    #     'fields': 'instagram_business_account',
    #     'access_token': access_token
    # }

    # resp = get(url, headers=headers, params=params)

    # print(resp.content)

    # if resp.status_code == 200 or resp.status_code == 201:
    #     resp = loads(resp.content)
    #     if 'instagram_business_account' in resp:
    #         instagram_business_account = resp['instagram_business_account']
    #         instagram_business_account = instagram_business_account['id']


    # GET THE USER ID AND NAME FROM THE ACCESS TOKEN

    # "https://graph.facebook.com/{graph-api-version}/
    # me/accounts?fields=instagram_business_account{id}

    
    logging.info('GET THE USER ID AND NAME FROM THE ACCESS TOKEN...')

    # me/accounts?fields=instagram_business_account
    # "data": [
    #     {
    #     "instagram_business_account": {
    #         "id": "17841453677786713"
    #     },
    #     "id": "105524828426133"
    #     }
    # ],
    # "paging": {
    #     "cursors": {
    #     "before": "MTA1NTI0ODI4NDI2MTMz",
    #     "after": "MTA1NTI0ODI4NDI2MTMz"
    #     }
    # }
    # }

    url = 'https://graph.facebook.com/v14.0/me/accounts'

    headers = {
        'Content-Type': 'application/json'
    }

    params = {
        'fields': 'access_token,instagram_business_account{id,name,profile_picture_url}',
        'access_token': access_token
    }

    resp = get(url, headers=headers, params=params)

    logging.info(resp.content)

    if resp.status_code == 200 or resp.status_code == 201:

        resp = loads(resp.content)

        logging.info(resp)

        instagram_business_account = resp['data'][0]['instagram_business_account']['id']
        page_id = resp['data'][0]['id']
        page_access_token = resp['data'][0]['access_token']
        page_name = resp['data'][0]['instagram_business_account']['name']
        profile_picture_url = resp['data'][0]['instagram_business_account']['profile_picture_url']


    else:
        page_access_token = ''
        page_id = ''
        page_name = ''
        instagram_business_account = ''
        profile_picture_url = ''


    # url = 'https://graph.facebook.com/v14.0/me'

    # headers = {
    #     'Content-Type': 'application/json'
    # }

    # params = {
    #     'fields': 'instagram_business_account',
    #     'access_token': page_access_token
    # }

    # resp = get(url, headers=headers, params=params)

    # print(resp.content)

    # if resp.status_code == 200 or resp.status_code == 201:

    #     resp = loads(resp.content)

    #     print(resp)

    #     if 'instagram_business_account' in resp['data'][0]:
    #         instagram_business_account = resp['instagram_business_account']['id']
    #         ig_name = resp['name']

    # else:
    #     instagram_business_account = ''
    #     ig_name = ''


    # GET LOCATION FROM THE ACCESS TOKEN

    # curl -i -X GET \
    # "https://graph.facebook.com/{graph-api-version}/{user-id}?    
    # fields=location{location{city,state,region_id}}&access_token={user-access-token}"


    # url = 'https://graph.facebook.com/v14.0/{}'.format(instagram_business_account)

    # params = {
    #     'fields': 'location{location{city,state,region_id}}',
    #     'access_token': access_token
    # }

    # resp = get(url, headers=headers, params=params)

    # if resp.status_code == 200 or resp.status_code == 201:
    #     resp = loads(resp.content)
    #     if 'location' in resp:
    #         location = resp['location']
    #         if 'id' in location:
    #             location_id = location['id']

    # else:
    #     location_id = ''

    account_details = dict()
    account_details['instagram_business_account'] = instagram_business_account
    account_details['user_id'] = instagram_business_account
    account_details['page_id'] = page_id
    # account_details['org_location_id'] = location_id
    account_details['account_name'] = page_name
    account_details['access_token'] = access_token
    account_details['profile_picture_url'] = profile_picture_url
    account_details['page_access_token'] = page_access_token
    date_now = str(datetime.utcnow()).split('.')[0]
    account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") 
    accounts_collection.find_one_and_update({"_id":ObjectId(state)},{"$set":account_details})

    return {'status': 'success'}



# GETS TEMPORARY ACCESS TOKEN

def get_temp_token(state):

    # https://levelup.gitconnected.com/automating-instagram-posts-with-python-and-instagram-graph-api-374f084b9f2b

    client_id = appConstants.instagram['INSTAGRAM_CLIENT_ID']

    logging.info(client_id)

    auth_url = 'https://www.facebook.com/v14.0/dialog/oauth'

    response_type = 'code'

    redirect_uri = appConstants.instagram['INSTAGRAM_REDIRECT_URL']

    scopes = [
            'business_management',
            'pages_show_list',
            'instagram_basic',
            'instagram_manage_insights',
            'pages_manage_posts',
            'public_profile',
            'instagram_content_publish',
            'pages_read_engagement',
            'instagram_manage_comments',
            'ads_management',
            'publish_video',
            'read_insights',
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
