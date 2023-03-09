from fastapi import APIRouter


router = APIRouter(
     tags=['Hidden'],   
)


def convert_to_json(file):
    i = 1
    result = {}
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            r = line.split('] [')
            result[i] = {'timestamp': r[0], 'level': r[1], 'thread': r[2], 'message': r[3]}
            i += 1

    return result

# GET LOGS
# REFERENCE: https://stackoverflow.com/questions/54689242/convert-log-file-into-json-file-using-python

@router.get('/logs', include_in_schema=False)
def get_logs():
    return convert_to_json('app/logfile.log')
