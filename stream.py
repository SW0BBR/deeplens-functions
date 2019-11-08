import cv2
vs = cv2.VideoCapture('/opt/awscam/out/ch2_out.mjpeg')
while True:
	check, framesmall = vs.read()
	# print(check,framesmall)
	framesmall = cv2.resize(framesmall, None, fx=0.4,fy=0.4)
	cv2.imshow("frame",framesmall)
	
	if cv2.waitKey(1) == ord('q'):
		break

vs.release()
