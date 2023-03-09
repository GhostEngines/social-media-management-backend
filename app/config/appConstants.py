
from os import environ

if 'host' not in environ:
    host = 'http://localhost:7000'
    # host = 'https://smm.herokuapp.com'
else:
    host = environ['host']


def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f()
    
    return property(fget, fset)


# LIST OF CONSTANT VARIABLES

class _Const(object):

    @constant
    def log_file():
        return "app/logs/app.log"

    @constant
    def sentry():
        return "https://2401504776cd43f5b0f77ede18025bd6@o1153670.ingest.sentry.io/6523078"

    @constant
    def filebase():

        filebase = {
            'USERNAME': 'Root Key',
            'KEY': 'A08E30A4C6CF530A0CFD',
            'SECRET': 'b8XaT7wPNwVk3RWSBcGch221kENlUAXldpQxs5UP',
            'ENDPOINT': 'https://smm.s3.filebase.com'
        }

        return filebase

    @constant
    def local_filebase():
        return './data/uploads/'

    @constant
    def local_cred_filebase():
        return './data/creds/'

    @constant
    def local_store_filebase():
        return './data/store/'

    @constant
    def allowed_extensions():
        return ['png', 'jpg', 'jpeg', 'gif', 'mp4']

    # FIREBASE

    @constant
    def firebase():
        
        config = {
        'apiKey': "AIzaSyAYveHlHK7256oNnsp08lYXfCyeENFHAqE",
        'authDomain': "smm-88d06.firebaseapp.com",
        'projectId': "smm-88d06",
        'storageBucket': "smm-88d06.appspot.com",
        'serviceAccount': "app/handlers/firebase.json",
        'databaseURL': "https://smm-88d06.firebaseio.com"
        #   'messagingSenderId': "570353119408",
        #   'appId': "1:570353119408:web:14d31adc1769f98e2a8b75",
        }

        return config   

    # LINKEDIN

    @constant
    def linkedin():

        data = {
            'LINKEDIN_CLIENT_ID': '86dl1xug1p1ymj',
            'LINKEDIN_CLIENT_SECRET': 'WBxbs8d5faozgi6r',
            'LINKEDIN_REDIRECT_URL': host + '/linkedin/callback'
        }

        return data
    
    # FACEBOOK

    @constant
    def facebook():
        data = {
            'FACEBOOK_CLIENT_ID': '550620925596337',
            'FACEBOOK_CLIENT_SECRET': '939e67ff2a89ea9bd29a0f37e72c0194',
            'FACEBOOK_REDIRECT_URL': host + '/facebook/login/callback'
        }

        return data          

    # INSTAGRAM

    @constant
    def instagram():
        data = {
            'INSTAGRAM_CLIENT_ID': '550620925596337',
            'INSTAGRAM_CLIENT_SECRET': '939e67ff2a89ea9bd29a0f37e72c0194',
            'INSTAGRAM_REDIRECT_URL': host + '/instagram/login/callback'
        }

        return data  

    # YOUTUBE

    @constant
    def youtube():
        data = {
            'YOUTUBE_CLIENT_ID': '693698869810-e00nl2hdtj3amrcb14elgcsf9n05kp58.apps.googleusercontent.com',
            'YOUTUBE_CLIENT_SECRET': 'uM9cqvklepiv2BcX4cWr7PGV',
            'YOUTUBE_REDIRECT_URL': host + '/youtube/callback'
        }

        return data  

    # YOUTUBE AUTHENTICATION

    @constant
    def youtube_auth():

        data = {
                    "web": {
                        'client_id': '693698869810-e00nl2hdtj3amrcb14elgcsf9n05kp58.apps.googleusercontent.com',
                        'client_secret': 'uM9cqvklepiv2BcX4cWr7PGV',
                        'redirect_uris': host + '/youtube/callback',
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://accounts.google.com/o/oauth2/token"
                    }
                }

        return data

    @constant
    def payment_gateway_credentials():
        data = {
            'api_id' : 'rzp_test_iMXY7AljB4NnjV',
            'api_secret': 'Ih6hqF4pc5DTpIrUu0SEFyB5'
        }

        return data

    @constant
    def subscription_options():
        data = {
            'basic': 'plan_JlE1YEZxx8KIK8',
            'pro': 'plan_JlE1tZnun3GaSi'
        }

        return data

    @constant
    def access_token_expire_minutes():
        return 3600

    @constant
    def secret_key():
        return 'NXX5vo91lp7FGmQ4E1GXOElwLSds8XP1'

    @constant
    def hash_algorithm():
        return 'HS256'

    @constant
    def default_time_zone():
        return 'UTC'

appConstants = _Const()