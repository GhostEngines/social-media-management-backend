# FIREBASE FUNCTIONS

from firebase_admin import credentials, initialize_app, storage
from app.config.appConstants import appConstants
import firebase_admin
from fastapi.logger import logger as logging

# REGULAR METHOD


# UPLOAD MEDIA TO FIREBASE 
# REFERENCE : https://medium.com/@abdelhedihlel/upload-files-to-firebase-storage-using-python-782213060064
# REFERENCE : https://stackoverflow.com/questions/68426892/why-i-get-this-error-on-python-firebase-admin-initialize-app


def upload_media(path):

    try:

        f_name = path.split('/')[-1]
        # Init firebase with your credentials
        cred = credentials.Certificate(appConstants.firebase['serviceAccount'])
        if not firebase_admin._apps:
            initialize_app(cred, {'storageBucket': appConstants.firebase['storageBucket']})

        f_name = path.split('/')[-1]
        logging.info(f_name)
        bucket = storage.bucket()
        logging.info(bucket)
        blob = bucket.blob(f_name)
        logging.info(blob)
        blob.upload_from_filename(path)

        blob.make_public()

        public_url = blob.public_url
        logging.info("your file url", public_url)    

        return ('url', public_url)

    except Exception as e:
        logging.exception('Exception occurred {}'.format(e))
        return ('error', 'Error uploading media {}'.format(e))    


# DELETE OBJECT
# REFERENCE : https://stackoverflow.com/questions/66665000/how-to-delete-a-image-file-from-google-firebase-storage-using-python

def delete_media(path):
    
    try:
        f_name = path.split('/')[-1]
        logging.info(f_name)
        logging.info('delete_media', path)
        cred = credentials.Certificate(appConstants.firebase['serviceAccount'])
        if not firebase_admin._apps:
            initialize_app(cred, {'storageBucket': appConstants.firebase['storageBucket']})
        
        bucket = storage.bucket()
        logging.info(bucket)
        blob = bucket.blob(f_name)
        logging.info(blob)
        blob.delete()

        return ('status', 'Deleted')

    except Exception as e:
        logging.exception('Exception occurred {}'.format(e))
        return ('error', 'Error uploading media {}'.format(e))   



# # PYREBASE METHOD - NOT WORKING

# from app.handlers import pyrebase
# from app.config.appConstants import appConstants

# # UPLOAD MEDIA TO FIREBASE 

# def upload_media(path):

#     try:

#         Firebase_storage = pyrebase.initialize_app(appConstants.firebase)
        
#         store = Firebase_storage.storage()

#         print(store)

#         f_name = path.split('/')[-1]
#         print(f_name, path)
#         store.child(f_name).put(path)

        

#         public_url = store.child(f_name).get_url(path)

#         print(public_url)
        
#         return public_url

#     except Exception as e:

#         return {'error': 'Error uploading media {}'.format(e)}

# # DELETE OBJECT

# def delete_media(path):

#     try:

#         Firebase_storage = pyrebase.initialize_app(appConstants.firebase)
#         path = path.split('/')[-1]
#         storage = Firebase_storage.storage()
#         storage.delete(path)

#         return {'status': 'Deleted'}
    
#     except Exception as e:

#         return {'error': 'Error uploading media {}'.format(e)}
