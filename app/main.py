from fastapi import FastAPI
from starlette.responses import FileResponse
from app.authenticate import routes as auth_routes
from app.user import routes as user_routes
from app.linkedin import routes as linkedin_routes
from app.instagram import routes as instagram_routes
from app.facebook import routes as facebook_routes
from app.youtube import routes as youtube_routes
from app.hidden_routes import routes as hidden_routes
from app.payments import routes as payment_routes
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from app.tasks.scheduled_tasks import run_scheduled_tasks
from fastapi.logger import logger as logging

# RESOURCES : https://stackoverflow.com/questions/60715275/fastapi-logging-to-file
logging.info('****************** Starting Server *****************')

app = FastAPI()
favicon_path = 'app/favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(linkedin_routes.router)
app.include_router(facebook_routes.router)
app.include_router(youtube_routes.router)
app.include_router(instagram_routes.router)
app.include_router(hidden_routes.router)
app.include_router(payment_routes.router)

scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: run_scheduled_tasks(),
    "interval",
    seconds = 10*60,
    id='J0001',
    name="Task Scheduler"
)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())
