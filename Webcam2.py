#!/usr/bin/env python3

# import
from sys import stdin, stdout
from imutils.video import VideoStream
from imutils import paths
import imutils
import cv2
import numpy as np
import urllib
import time
from math import *

# Declare variables
## ALL MEASUREMENTS ARE IN METRES

url = 'http://192.168.0.102:8080/'
#url = 'http://192.168.2.64:8080/'
# url = 'http://192.168.86.61:8080/'

base = False
start = False
test = False
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
# xBase, yBase = 240, 640
factor = 0.00326  # 1 pixel = 0.18 cm
heightCam = 1.41
heightOrg = 1.015
# f = open("values.txt", "a+")

# Colour mask
blueUpper = (120, 255, 255)
blueLower = (80, 100, 100) #actually 80

greenUpper = (60, 255, 255)
greenLower = (30, 120, 40)

# Initialize values (the initial values don't actually matter)
center = (0, 0)
radius = 1
orgRad = 1
focLength = 500
height = heightOrg


# Define mouse click event
def click(event, x, y, flags, param):
    global xcoord, ycoord
    global circen

    # Mouse click
    if event == cv2.EVENT_LBUTTONDOWN:
        # get x,y coordinates
        xcoord = x
        ycoord = y

        cv2.circle(img, (xcoord, ycoord), 10, (0, 0, 255), -1)

        cv2.imshow('Image', img)


def measure(x, y, armx, army, testx, testy, h, xg, yg):
    # print("a", xBase, yBase, x, y, armx, army)
    global angle, distance

    # Determine relative x+y distance
    xrel = (x - xBase) * factor
    yrel = (y - yBase) * -1 * factor

    # Determine relative arm x+y distance
    xarel = (armx - xBase) * factor
    yarel = (army - yBase) * -1 * factor

    # Determine relative test x+y distance
    xtrel = (testx - xBase) * factor
    ytrel = (testy - yBase) * -1 * factor

    print(xBase, yBase, xg, yg)

    # Determine relative claw x+y distance
    xcrel = (xg - xBase) * factor
    ycrel = (yg - yBase) * -1 * factor

    # Determine angle and distance of coordinate
    if xrel != 0:
        angPt = degrees(atan(yrel / xrel))
        if angPt < 0:
            angPt += 180
    else:
        angPt = 90

    # Determine angle and distance of ball
    if xarel != 0:
        angBall = degrees(atan(yarel / xarel))
        if angBall < 0:
            angBall += 180
    else:
        angBall = 90

    # Determine angle and distance of ball
    if xcrel != 0:
        angClaw = degrees(atan(ycrel / xcrel))
        if angClaw < 0:
            angClaw += 180
    else:
        angClaw = 90
    
    if (xg+1.0) < 0.1:
        angClaw = 0.0

    # Determine angle of testing station
    if xtrel != 0:
        angTest = degrees(atan(ytrel / xtrel))
        if angTest < 0:
            angTest += 180
    else:
        angTest = 90

    # Determine distance of coord and ball
    distPt = sqrt(xrel ** 2 + yrel ** 2)
    distBall = sqrt(xarel ** 2 + yarel ** 2)
    distTest = sqrt(xtrel ** 2 + ytrel ** 2)

    # print(angTest, distTest)
    # print(angClaw)

    # Displays values and exports them into a text file
    mystr = ("%.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f" % (
    xrel, yrel, angPt, distPt, angBall, distBall, h, angTest, distTest, angClaw))
    # stdout.write(mystr + '\n')

    f = open("values.txt", "a+")
    f.write(mystr + '\n')
    f.close()


#### MAIN #########################

# Creates Windows
window = cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Image', 480, 640)
cv2.moveWindow('Image', 500, 50)
cv2.setMouseCallback('Image', click)
window2 = cv2.namedWindow('LiveStream', cv2.WINDOW_NORMAL)
cv2.resizeWindow('LiveStream', 480, 640)
cv2.moveWindow('LiveStream', 10, 50)

# Creates stream
stream = cv2.VideoCapture(url + 'video')
xg, yg = -1.0, -1.0

# Start stream
i = 1
while (True):
    ret, frame = stream.read()
    cv2.putText(frame, 'Press \'q\' to exit.', (10, 600), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, 'Battery 1: 6.05 V', (10, 20), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, 'Battery 2: 5.94 V', (10, 40), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    # Still image on 50th frame
    if i == 50:
        img = frame
        cv2.imwrite("img.png", img)
        cv2.putText(img, 'Steps:', (10, 500), font, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, '   1. Click on the base location and press \'b\'.', (10, 520), font, 0.6, (255, 255, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(img, '   2. Click on the testing station location and press \'t\'.', (10, 540), font, 0.6,
                    (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, '   3. Click on the soil sample location and press \'s\'.', (10, 560), font, 0.6,
                    (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, 'Press \'d\' to delete the point.', (10, 580), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imwrite("stillframe.png", img)
        cv2.imshow('Image', img)

    # Display point on livestream feed
    if base == True:
        cv2.circle(frame, (xBase, yBase), 10, (0, 0, 255), -1)
        cv2.putText(frame, 'Base', (xBase + 10, yBase + 10), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    if start == True:
        cv2.circle(frame, (xsoil, ysoil), 10, (0, 0, 255), -1)
        cv2.putText(frame, 'Soil Sample', (xsoil + 10, ysoil + 10), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    if test == True:
        cv2.circle(frame, (xTest, yTest), 10, (0, 0, 255), -1)
        cv2.putText(frame, 'Testing Station', (xTest + 10, yTest + 10), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Colour Motion Detector
    # blurred = cv2.GaussianBlur(frame, (15, 15), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # displays mask of blue colour
    # cv2.imshow("mask", mask)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:3]  # Sort 3 largest contours

    # only proceed if at least one contour was found
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)

        # only proceed if there are not too many edge points
        if len(approx) > 1:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            ((xg, yg), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            # print(int(x), int(y))

            break
            
    #if len(cnts) == 0:
        #xg = -1
        #syg = -1

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # displays mask of blue colour
    # cv2.imshow("mask", mask)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:3]  # Sort 3 largest contours

    # only proceed if at least one contour was found
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)

        # only proceed if there are not too many edge points
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)

        # cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)), (255,255,0), 2)

        if ar >= 0.6 and ar <= 1.4:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            cv2.putText(frame, 'Arm', (center[0] + 12, center[1] + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            # print(int(x), int(y))

            # Displays coordinates every 20th frame
            if start == True and i % 10 == 0:
                measure(xsoil, ysoil, int(x), int(y), xTest, yTest, height, int(xg), int(yg))

            break

    # Initialize initial focal length
    if i == 5:
        focLength = (radius * (heightCam - heightOrg)) / orgRad

    # Calculates height
    elif i >= 5 and i % 20 == 0:
        height = heightCam - orgRad * focLength / radius

    # Displays height
    if i >= 5:
        cv2.putText(frame, "%.02fm" % height,
                    (frame.shape[1] - 250, frame.shape[0] - 20), cv2.FONT_HERSHEY_PLAIN,
                    2.0, (0, 255, 0), 3)

    # Stream live video
    cv2.imshow('LiveStream', frame)

    # Counter
    i += 1

    # Break out of loop
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    elif key == ord('d') and start == False:
        point = False
        circen = []
        img = cv2.imread('stillframe.png', -1)
        if base == True:
            cv2.circle(img, (xBase, yBase), 10, (0, 0, 255), -1)
            cv2.putText(img, 'Base', (xBase + 12, yBase + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            base == False
        if test == True:
            cv2.circle(img, (xTest, yTest), 10, (0, 0, 255), -1)
            cv2.putText(img, 'Testing Station', (xTest + 12, yTest + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            test == False
        cv2.imshow('Image', img)

    elif key == ord('b') and base == False:
        xBase = xcoord
        yBase = ycoord
        cv2.putText(img, 'Base', (xBase + 12, yBase + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Image', img)
        base = True

    elif key == ord('t') and base == True and test == False:
        xTest = xcoord
        yTest = ycoord
        cv2.putText(img, 'Testing Station', (xTest + 12, yTest + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Image', img)
        test = True

    elif (key == ord('s') and start == False and test == True):
        # try:
        xsoil = xcoord
        ysoil = ycoord
        cv2.putText(img, 'Soil Sample', (xsoil + 12, ysoil + 5), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('Image', img)

        # Call measure function
        # measure(xcoord, ycoord, x, y, height)
        measure(xsoil, ysoil, xBase, yBase, xTest, yTest, height, int(xg), int(yg))
        start = True
        stfile = open("start.txt", "w+")
        stfile.write("1")
        stfile.close()

        #Save soil image with colour reference
        soil = cv2.imread("stillframe.png", -1)
        cropped = soil[ycoord - 50:ycoord + 50, xcoord - 50:xcoord + 50]
        colour = cv2.imread("ColourReferenceScale.jpg", -1)
        r = 100.0 / colour.shape[1]
        dim = (100, int(colour.shape[0] * r))
        resized = cv2.resize(colour, dim, interpolation=cv2.INTER_AREA)
        vertical = np.concatenate((cropped, resized), axis=0)
        cv2.imwrite("SoilColour.jpg", vertical)
        #except:
        # If no coordinate points were initialized
        #print("No coordinate point was specified.")
# f.close()
cv2.destroyAllWindows()