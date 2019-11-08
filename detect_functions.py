from PIL import Image
from datetime import datetime
import face_recognition as fr
import numpy as np
import os, cv2, face_recognition, pytz, requests

def get_encoded_faces():
    """
    looks through the faces folder and encodes all
    the faces

    :return: dict of (name, image encoded)
    """
    encoded = {}

    for dirpath, dnames, fnames in os.walk("./faces"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png"):
                face = fr.load_image_file("faces/" + f)
                encoding = fr.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding

    return encoded


def unknown_image_encoded(img):
    """
    encode a face given the file name
    """
    face = fr.load_image_file("faces/" + img)
    encoding = fr.face_encodings(face)[0]

    return encoding


def calc_faces():
    """ Creates encodings for the known faces in /faces.
    -output: known_faces_encoded : list containing face encodings
             known_faces_names: list containing labels of faces"""


    print("Calculating face properties ...")
    # Calculate known face properties from /faces
    face_dict = get_encoded_faces()
    known_faces_encoded =  list(face_dict.values())
    known_faces_names = list(face_dict.keys())

    return known_faces_encoded, known_faces_names

def recog_faces_frame(known_faces_encoded, known_faces_names,vs):
    """ Detects and draws faces in one frame.

    -output: faces_detected: list of strings describing faces that were detected in the image.
             frame: np array of the final image with bounding boxes around detected faces."""
    face_locations = []
    img_face_encodings = []
    faces_detected = []

    # Capture webcam
    check, frame = vs.read()

    if check:
        # Resize for quicker detect
        small_frame = cv2.resize(frame,(0,0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Detect and calculate face properties in every other frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        img_face_encodings = face_recognition.face_encodings(rgb_small_frame,face_locations)

        faces_detected = []
        for encoding in img_face_encodings:
            name = "Unknown"
            # Check if face matches to existing encodings
            matches = face_recognition.compare_faces(known_faces_encoded, encoding)
            face_distances = face_recognition.face_distance(known_faces_encoded, encoding)
            best_index = np.argmin(face_distances)
            # Add name if match was found
            if matches[best_index]:
                name = known_faces_names[best_index]
            faces_detected.append(name)

        # Save frame without bboxes
        frame_noBB = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        for (top, right, bottom, left), name in zip(face_locations, faces_detected):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around detected face
            cv2.rectangle(frame, (int(left-20), int(top-20)), (int(right+20), int(bottom+20)), (255, 0, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left-20, bottom -15), (right+20, bottom+20), (255, 0, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left -20, bottom + 15), font, 1.0, (255, 255, 255), 2)
            # cv2.imshow('Video', frame)
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    else:
        print("Camera stuck, restarting...")
        return None, None, None

    return faces_detected, frame, frame_noBB

def get_cur_time(only_date=False):
    if not only_date:
        timezone_ams = pytz.timezone('Europe/Amsterdam')
        cur_time = datetime.now(timezone_ams)
        return cur_time.strftime('%Y-%m-%d / %H:%M:%S:%f')[:-3]
    else:
        timezone_ams = pytz.timezone('Europe/Amsterdam')
        cur_time = datetime.now(timezone_ams)
        return cur_time.strftime('%Y-%m-%d')

def get_init_comment(names):
    init_comment = "Ding dong! "
    if len(names) == 2:
        init_comment += "{} and {} are at the door.".format(names[0],names[1])
    elif len(names) > 2:
        faces_count = 1
        for name in names:
            if len(names) - faces_count > 0:
                init_comment += "{}, ".format(name)
                faces_count += 1
            else:
                init_comment += "and {} are at the door.".format(name)
    else:
        init_comment += "{} is at the door.".format(names[0])
    return init_comment

def upload_frame(frame, init_comment, cur_time):
    im = Image.fromarray(frame)
    im.save("doorman.jpg")

    image = {
            'file' : ('doorman.jpg', open('doorman.jpg', 'rb'), 'jpg')
            }

    slack_token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ["SLACK_CHANNEL"]
        
    payload={
        "filename":"doorman.jpg", 
        "token": slack_token, 
        "channels":[channel],
        'title': '{}'.format(cur_time),
        'initial_comment': init_comment
        }

    requests.post(url='https://slack.com/api/files.upload', params=payload, files=image)
    print("Done.")

