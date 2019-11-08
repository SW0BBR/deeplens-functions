from detect_functions import *
from PIL import Image
import numpy as np
import cv2, requests, time, os

face_database = []
known_faces_encoded, known_face_names = calc_faces()
vs = cv2.VideoCapture('/opt/awscam/out/ch2_out.mjpeg')
last_seen = []
print("Detecting, comparing and drawing faces ...")
while True:
    # Check for lockfiles
    if os.path.isfile('./calc_faces.txt'):
      os.remove('calc_faces.txt')
      known_faces_encoded, known_face_names = calc_faces()

    if os.path.isfile('./stop.txt'):
        os.remove('stop.txt')
        print("Stop exists")
        break

    names, frame, frame_noBB = recog_faces_frame(known_faces_encoded, known_face_names, vs)

    if names:
      print("{} detected, ".format(names), end='')

      # Add to database
      cur_time_full = get_cur_time()
      cur_time_date = get_cur_time(True)
      face_database.append((np.array(names),cur_time_full))
      
      # Prepare unknown faces to be labeled by slack chat
      if 'Unknown' in names:
        im = Image.fromarray(frame_noBB)
        im.save("unknown@{}.jpg".format(cur_time_date))

      # Don't show the same face
      if last_seen == names:
         print("skipping ...")
         continue

      # Upload to slack
      print("uploading to slack ...")
      init_comment = get_init_comment(names)
      upload_frame(frame, init_comment, cur_time_full)

      last_seen = names

    elif names == None:
      vs.release()
      vs.open()
      continue

    elif not names:
      print("Nobody at the door at {}".format(get_cur_time()))


print("Exiting...")
cv2.destroyAllWindows()
np.save("faces_{}".format(get_cur_time(only_date=True)),face_database)
