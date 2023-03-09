import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from app.config.appConstants import appConstants
from fastapi.logger import logger as logging

def get_and_store_creds(user_id):

    credentials = None

    CRED_DIRECTORY = appConstants.local_cred_filebase

    cred_path = CRED_DIRECTORY + user_id + '.pickle'

    if os.path.exists(cred_path):
        with open(cred_path, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logging.info('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            logging.info('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                appConstants.local_store_filebase + 'client_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                authorization_prompt_message='Authorize smm to access your YouTube account?')
            
            flow.credentials
            credentials = flow.credentials

            # Save the credentials for the next run
            with open(cred_path, 'wb') as f:
                logging.info('Saving Credentials...')
                pickle.dump(credentials, f)

    return {'status': 'success'}
