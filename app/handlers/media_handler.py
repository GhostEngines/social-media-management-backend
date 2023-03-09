import cv2


def media_handler(type, media_path, extension):

    if extension == 'jpeg' or extension == 'png' or extension == 'jpg':
        props = get_image_props(media_path)
        result = get_result(type, props, 'image')
    
    elif extension == 'mp4' or extension == 'mov':
        props = get_video_props(media_path)
        result = get_result(type, props, 'video')
    
    else:
        props = ''
        result = ('Abort', 'Not a valid file type')

    return result

# GETS IMAGE PROPERTIES
# https://www.geeksforgeeks.org/how-to-find-width-and-height-of-an-image-using-python/

def get_image_props(file_path):
    image = cv2.imread(file_path)
    height, width = image.shape[:2]
    return (height, width)

# GETS VIDEO PROPERTIES 
# https://stackoverflow.com/questions/7348505/get-dimensions-of-a-video-file

def get_video_props(file_path):
    vid = cv2.VideoCapture(file_path)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    return (height, width)

# GET VALIDATED

def get_result(type, props, media_type = ''):
    abort = False
    state = 'Expected media aspects received'

    if type == 'instagram' and media_type == 'image':
    
        if props[1] < 320 or props[1] < 1080:
            abort = True

        if props[0] < 566 or props[0] > 1350:
            abort = True

        ratio = props[0]/props[1]

        if ratio >= 1.91 or ratio < 0.2:
            abort = True
    
    elif type == 'instagram' and media_type == 'video':

        if props != (1080,1080) and props != (1350,1080):
            abort = True


    if abort == True and type == 'instagram':
        state = 'Accepted image aspects: Aspect ratio: between 1.91:1 and 4:5, Width: between 320 and 1,080 pixels, Height: between 566 and 1,350 pixels. Accepted video aspects: 1080 x 1080 pixels (landscape) 1080 x 1350 pixels (portrait)'
        return ('Abort', state)
    
    return ('Proceed', state)

# type = 'instagram'
# # file_path = 'data/uploads/insta.jpg'
# file_path = 'data/uploads/video.mp4'

# print(media_handler(type, file_path))
