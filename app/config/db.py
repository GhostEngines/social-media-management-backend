# IMPORT MONGODB

from pymongo import MongoClient
from fastapi.logger import logger as logging

# conn = MongoClient()

conn = MongoClient('mongodb+srv://heroku:1aouMoHCpw8qccc8@cluster0.vdxsnlz.mongodb.net/?retryWrites=true&w=majority', connect=False)

dblist = conn.list_database_names()

if "smm" in dblist:
    logging.info("The database exists.")

accounts_collection = conn.smm.accounts
user_collection = conn.smm.users
account_activities_collection = conn.smm.account_activities
tasks = conn.smm.tasks
