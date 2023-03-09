from uuid import uuid4
from app.config.appConstants import appConstants
from fastapi import FastAPI
from app.utils.logging import logging, sentry_setup
from app.config.db import initialize_db
from os import environ
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    
    title= appConstants.appDetails['TITLE'],
    version = appConstants.appDetails['VERSION'],
    description = appConstants.appDetails['APP_DESCRIPTION'],
    terms_of_service = appConstants.appDetails['TC_URL'],
    contact = {
                'email': appConstants.appDetails['CONTACT_EMAIL'],
                'url': appConstants.appDetails['CONTACT_URL'],
                'name': appConstants.appDetails['CONTACT_NAME']
            },
    )

# admin = FastAPI(
#     title = appConstants.adminAppDetails['TITLE'],
#     version = appConstants.adminAppDetails['VERSION'],
#     description = appConstants.adminAppDetails['APP_DESCRIPTION'],
#     terms_of_service = appConstants.adminAppDetails['TC_URL'],
#     contact = {
#                 'email': appConstants.adminAppDetails['CONTACT_EMAIL'],
#                 'url': appConstants.adminAppDetails['CONTACT_URL'],
#                 'name': appConstants.adminAppDetails['CONTACT_NAME']
#             },
#     )


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 


# admin.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# ) 


# SENTRY SETUP
sentry_setup()
logging('****************** Starting Server *****************', 'info')


# INITIALIZE MONGODB
initialize_db()


# LOGGING SETUP

def logging_setup():
    if appConstants.environmental_variables['PRODUCTION'] == True:
        logging("Running in production mode", 'info')
    else:
        logging("Running in development mode", 'info')
        environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    return {'status': 'success'}


# SETUP ROUTES AND SCHEDULER

def setup_routes_and_scheduler():
    if appConstants.environmental_variables['WORKER'] == False:
        from fastapi import Request
        from app.authenticate import routes as auth_routes
        from app.user import routes as user_routes
        from app.projects import routes as project_routes
        from app.tasks import routes as task_routes
        from app.assets import routes as assets_routes
        from app.linkedin import routes as linkedin_routes
        from app.instagram import routes as instagram_routes
        from app.facebook import routes as facebook_routes
        from app.youtube import routes as youtube_routes
        from app.google_analytics import routes as google_analytics_routes
        from app.whatsapp import routes as whatsapp_routes
        from app.payments import routes as payment_routes
        # from app.internal.admin import routes as admin_routes
        from app.twitter import routes as twitter_routes
        from app.notifications import routes as notification_routes
        from sentry_sdk import push_scope, capture_exception
        from starlette.middleware.sessions import SessionMiddleware
        
        # from app.utils.scheduler import run_scheduled_tasks_using_thread
        # run_scheduled_tasks_using_thread()



        # COOKIES
        # DOCUMENTATION: https://www.starlette.io/responses/#set-cookie

        app.add_middleware(
            SessionMiddleware, 
            secret_key = appConstants.app_secrets['COOKIES_RANDOM_SECRET'],
            )
        
        @app.middleware("http")
        async def sentry_exception(request: Request, call_next):
            if 'user_id' in request.cookies:
                user_id = request.cookies['user_id']
            else:
                user_id = str(uuid4().hex)

            try:
                response = await call_next(request)
                return response
            except Exception as e:
                with push_scope() as scope:
                    scope.set_context("request", request)
                    user_id = user_id
                    scope.user = {
                        "ip_address": request.client.host,
                        "id": user_id
                    }
                    capture_exception(e)
                raise e


        # ROUTES SETUP

        @app.get('/', include_in_schema = False)
        def home(request: Request):
            if 'username' in request.cookies:
                return {'status': 'Welcome to smm, {}'.format(request.cookies['username'])}
            return {'status':'OK'}

        app.include_router(auth_routes.router)
        app.include_router(user_routes.router)
        app.include_router(project_routes.router)
        app.include_router(task_routes.router)
        app.include_router(assets_routes.router)
        app.include_router(whatsapp_routes.router)
        app.include_router(linkedin_routes.router)
        app.include_router(facebook_routes.router)
        app.include_router(instagram_routes.router)
        app.include_router(youtube_routes.router)
        app.include_router(google_analytics_routes.router)
        app.include_router(twitter_routes.router)
        app.include_router(notification_routes.router)
        app.include_router(payment_routes.router)
        
        # INCLUDE IN ADMIN ROUTER
        # admin.include_router(auth_routes.router)
        # admin.include_router(user_routes.router)
        # admin.include_router(admin_routes.router)

        # MOUNT ADMIN ROUTER
        # app.mount('/admin', admin)
        

    else:
        from app.utils.scheduler import run_scheduled_tasks_using_thread
        run_scheduled_tasks_using_thread()
    
    return {'status':'OK'}


# RUN SETUP

logging_setup()
setup_routes_and_scheduler()