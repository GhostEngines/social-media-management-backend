# LINKEDIN FUNCTIONS

from requests import post, get, exceptions
from json import loads
from app.config.appConstants import appConstants
from datetime import datetime
from bson import ObjectId
from app.config.db import accounts_collection
from requests.utils import unquote
from requests_oauthlib import OAuth2Session
from fastapi.logger import logger as logging


# DECODE THE CODE AND GET THE ACCESS TOKEN, REFRESH TOKEN, USER ID AND STORE IN DB 

def get_access_token(request):
    
    # GET THE STATE AND CODE FROM THE REQUEST

    try:
        query_url = str(request.query_params)
        query_url = str(unquote(query_url)).split('&')
        for elem in query_url:
            if 'state' in elem:
                lis = elem.split('+')
                for i in range(len(lis)):
                    if 'state' in lis[i]:
                        state = lis[1+i].strip().replace('\'', '').replace(',', '')
        logging.info('state: ' , state)
        code = request.query_params.get('code')
        logging.info(code)
    
    except:
        return {'status': 'Error'}

    state = str(state)


    # GET THE ACCESS TOKEN AND STORE
    
    client_id = appConstants.linkedin['LINKEDIN_CLIENT_ID']
    client_secret = appConstants.linkedin['LINKEDIN_CLIENT_SECRET']

    grant_type = 'authorization_code'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

    redirect_uri = appConstants.linkedin['LINKEDIN_REDIRECT_URL']

    params = {
        'grant_type': grant_type,
        'redirect_uri': redirect_uri,
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret
    }


    resp = None

    try:
        resp = post(access_token_url, params=params, headers=headers, timeout=10)
    
    except exceptions.ConnectionError:
        return


    if resp.status_code == 200:
        resp = loads(resp.text)
        
        if 'access_token' in resp:
            access_token = resp['access_token']
        
        if 'refresh_token' in resp:
            refresh_token = resp['refresh_token']

    else:
        access_token = ''
        refresh_token = ''
    

    # GET AND STORE MY DETAILS
    # https://api.linkedin.com/v2/me

    try:
        base_url = 'https://api.linkedin.com/v2/me'

        header = {
            'Authorization': 'Bearer {}'.format(access_token)
        }

        resp = get(base_url, headers=header)

        if resp.status_code == 200:
            resp = loads(resp.text)

        if 'id' in resp:
            user_id = resp['id']

    except:
        user_id = ''
    
    account_details = dict()
    account_details['access_token'] = access_token
    account_details['refresh_token'] = refresh_token
    account_details['my_id'] = user_id
    date_now = str(datetime.utcnow()).split('.')[0]
    account_details['latest_update'] = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") 
    accounts_collection.find_one_and_update({"_id":ObjectId(state)},{"$set":account_details})

    return {'status': 'success'}


# GETS TEMPORARY ACCESS TOKEN

def get_temp_token(state):

    client_id = appConstants.linkedin['LINKEDIN_CLIENT_ID']

    auth_url = 'https://www.linkedin.com/oauth/v2/authorization'

    scopes = [
                'r_organization_social',
                'w_member_social',
                'w_organization_social',
                'r_member_social',
                'r_compliance',
                'w_compliance',
                'rw_organization_admin',
                'r_1st_connections_size',
                'r_ads_reporting',
                'r_emailaddress',
                'r_liteprofile',
                'r_basicprofile',
                'r_ad',
                'rw_ads'
            ]

    fin_scope = ''

    for scope in scopes:
        fin_scope += scope + ','

    # scope = 'r_organization_social,rw_organization_admin,r_1st_connections_size,r_ads_reporting,r_emailaddress,r_liteprofile,r_basicprofile,rw_ads,w_member_social,w_organization_social'

    response_type = 'code'

    redirect_uri = appConstants.linkedin['LINKEDIN_REDIRECT_URL']

    params = {
        'response_type': response_type,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': fin_scope[:-1],
        'client_id': client_id
    }

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
                          scope=scope)
    
    authorization_url, _ = oauth.authorization_url(auth_url, params)
    
    return str(authorization_url) + '&state={}'.format(state)



'''

def get_page_stats_linkedin(org_id, access_token):

    from requests import get
    from json import loads

    #     curl -X GET 'https://api.linkedin.com/v2/organizationPageStatistics?q=organization&organization={organization URN}' \
    # -H 'Authorization: Bearer {INSERT_TOKEN}'

    base_url = 'https://api.linkedin.com/v2/organizationPageStatistics'

    params = {
        'q': 'organization',
        'organization': org_id
    }

    header = {'Authorization': 'Bearer {}'.format(access_token)}

    resp = get(base_url, params=params, headers=header)

    if resp.status_code == 200:
        resp = loads(resp.text)

    # print(resp.content)

    return resp

'''