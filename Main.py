'''
Code for perspective transformation and circle track with color filtering.

This code was adapted from:

        -(Perspective transformation by Muhammad Salar Khan): https://gist.github.com/TheSalarKhan/9af70004caf2a5ee5ec5
        -(Color filtering by gsnikitin[youtube]):https://pastebin.com/NkUTXM8T

'''

import numpy as np
import cv2

# top left, top right, bottom left, bottom right
pts = [(0,0),(0,0),(0,0),(0,0)]
pointIndex = 0

cam = cv2.VideoCapture(0)

_,img = cam.read()


# Aspect ratio for an A4 sheet. 1:1.414
# 500 * 1.414 = 707, that is why I chose this size.
ASPECT_RATIO = (500,707)

pts2 = np.float32([[0,0],[ASPECT_RATIO[1],0],[0,ASPECT_RATIO[0]],[ASPECT_RATIO[1],ASPECT_RATIO[0]]])
# mouse callback function
def draw_circle(event,x,y,flags,param):
	global img
	
	global pointIndex
	global pts

	if event == cv2.EVENT_LBUTTONDBLCLK:
		cv2.circle(img,(x,y),0,(255,0,0),-1)
		pts[pointIndex] = (x,y)
		pointIndex = pointIndex + 1

def selectFourPoints():
	global img
	global pointIndex
	

	print "Please select 4 points, by double clicking on each of them in the order: \n\
	top left, top right, bottom left, bottom right."
	

	while(pointIndex != 4):
		_,imge = cam.read() 
		cv2.imshow('image',imge)
		key = cv2.waitKey(20) & 0xFF
		if key == 27:
			return False

	return True


cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)

while(1):
        
	if(selectFourPoints()):

		# The four points of the A4 paper in the image
		pts1 = np.float32([\
			[pts[0][0],pts[0][1]],\
			[pts[1][0],pts[1][1]],\
			[pts[2][0],pts[2][1]],\
			[pts[3][0],pts[3][1]] ])

		M = cv2.getPerspectiveTransform(pts1,pts2)

		while(1):

                        #Get video frame
			_,frame = cam.read()

                        #Transform the perspective
			pers = cv2.warpPerspective(frame,M,(707,500))

                        #Transform color from BGR to HSV
			img_hsv=cv2.cvtColor(pers, cv2.COLOR_BGR2HSV)

			# lower mask (0-10)
			lower_red = np.array([105,105,104])
			upper_red = np.array([255,255,255])

			#Apply the color range filter
			res = cv2.inRange(img_hsv, lower_red, upper_red)

			#Create kernel with 5x5 pixels
			kernel = np.ones((5,5),np.uint8)

			#Create mask for noise filtering
			mask = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
			mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

			 
			# find contours in the mask and initialize the current
			# (x, y) center of the ball
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
			center = None

			# only proceed if at least one contour was found
			if len(cnts) > 0:
				# find the largest contour in the mask, then use
				# it to compute the minimum enclosing circle and
				# centroid
				c = max(cnts, key=cv2.contourArea)
				((x, y), radius) = cv2.minEnclosingCircle(c)
				M_ = cv2.moments(c)
				center = (int(M_["m10"] / M_["m00"]), int(M_["m01"] / M_["m00"]))

		
				if radius > 10:
					# draw the circle and centroid on the frame,
					# then update the list of tracked points
					cv2.circle(pers, (int(x), int(y)), int(radius),(0, 255, 255), 2)
					cv2.circle(pers, center, 3, (0, 0, 255), -1)
					cv2.putText(pers,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
					cv2.putText(pers,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)

                        #Image of the circle tracking
			cv2.imshow('Circle Track', pers)

			#Image of the color mask
			cv2.imshow('Color Mask', mask)


			key = cv2.waitKey(10) & 0xFF
			if key == 27:
				break
	else:
		print "Exit"

	break
	# cv2.imshow('image',img)
	# if cv2.waitKey(20) & 0xFF == 27:
	# 	break
cam.release()
cv2.destroyAllWindows()
