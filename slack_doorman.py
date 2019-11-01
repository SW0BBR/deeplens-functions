from detect_functions import *
from PIL import Image
import numpy as np
import cv2, requests, time

face_database = []
known_faces_encoded, known_face_names = calc_faces()

print("Detecting, comparing and drawing faces ...")
while True:
    names, frame, frame_noBB = recog_faces_frame(known_faces_encoded, known_face_names)
    if names:
        print("Face detected, uploading to slack ...")
        # cv2.imshow("detected face",cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        # Add to database
        cur_time_full = get_cur_time()
        cur_time_date = get_cur_time(True)
        face_database.append((np.array(names),cur_time_full))

        if 'Unknown' in names:
            im = Image.fromarray(frame_noBB)
            im.save("unknown@{}.jpg".format(cur_time_date))
            known_faces_encoded, known_face_names = calc_faces()

        # Upload to slack
        init_comment = get_init_comment(names)
        upload_frame(frame, init_comment, cur_time_full)
        time.sleep(3)
    if cv2.waitKey(1) == ord('q'):
        break
    
cv2.destroyAllWindows()
np.save("faces_{}".format(get_cur_time(only_date=True)),face_database)
print("Shutting down ...")

        
