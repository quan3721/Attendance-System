import os
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import cvzone
from ultralytics import YOLO
import time
from reset_date import reset_data
from export_Data import *
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("../Database_Firebase/attendance-system-f3c35-firebase-adminsdk-s7c8b-2b1990099a.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://attendance-system-f3c35-default-rtdb.asia-southeast1.firebasedatabase.app/',
})

##### Webcam #############
cap = cv2.VideoCapture(0)
cap.set(3,640) ### width of camera
cap.set(4,480) ### height of camera
# cap.set(10,150) ### set brightness of camera

##### Hand Detection ######
# ---- maxHands : số lượng bàn tay ---- #
# ---- detectionCon : độ tin cậy ---- #
hand_detector = HandDetector(maxHands=1,detectionCon=0.7)

##### Image Background ############
imgBackground = cv2.imread('../Resources/background.png')
# print(imgBackground)

##### Import a list contain the value of each images for attendance system ####
folderPathModes = '../Resources/Modes'
listPathModes = os.listdir(folderPathModes)
#print(listPathModes) ## test để xem listPathModes có gì
listImageModes = []
for imagePathModes in listPathModes:
    listImageModes.append(cv2.imread(os.path.join(folderPathModes,imagePathModes)))
# print(listImageModes)
###############################################################################

##### Load Model trained ##################
model = YOLO('../models/best.pt')
classNames = ['Fake', 'Quan']

############ Một vài thông số ##############
counter = 0
selectionSpeed = 5
selection = -1
modePositions = [(1016,238),(1016,438)]
colorMode = [(0,255,0), (0,0,255)]
indexImageMode = 0
pauseCounter = 0
confidence = 0.7
id = 0
count = 0
selectINorOut = 0
prev_frame_time = 0
new_frame_time = 0
###########################################

while True:
    new_frame_time = time.time()
    success, img = cap.read()

    ### Display the Webcam ###
    # cv2.imshow('camera',img)
    imgBackground[160:160 + 480, 53:53 + 640] = img

    ### Display the image Mode ###
    imgBackground[44:44+633, 808:808+414] = listImageModes[indexImageMode]

    ### Process first mode ######
    if indexImageMode == 0 :
        ### Detect Hand ######
        hands, img = hand_detector.findHands(img)
        # print(hands)
        if hands and pauseCounter == 0 :
            hand1 = hands[0]
            # print(hand1)
            finger1 = hand_detector.fingersUp(hand1)
            # print(finger1)

            if finger1 == [0,1,0,0,0]:
                if selection != 1:
                    counter = 1
                selection = 1
            elif finger1 == [0,1,1,0,0]:
                if selection != 2:
                    counter = 1
                selection = 2
            else :
                selection = -1
                counter = 0

            if counter > 0 :
                counter += 1
                #print(counter)
                #### create a ellipse for selection ####
                cv2.ellipse(imgBackground, modePositions[selection-1], (77,77),0,0,
                            counter*selectionSpeed, colorMode[selection-1],15)
                selectINorOut = selection
                if counter * selectionSpeed > 360:
                    counter = 1
                    selection = -1
                    indexImageMode +=1
                    pauseCounter = 1


        if pauseCounter > 0:
            pauseCounter +=1
            if pauseCounter > 130:
                pauseCounter = 0

    ################### Next mode ####################
    else:
        results = model(img, stream=True, verbose=False)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                ### bounding box ####
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                w, h = x2 - x1, y2 - y1
                ### confidence ######
                conf = math.ceil((box.conf[0] * 100)) / 100
                # print(conf)
                ### class Name ######
                cls = int(box.cls[0])

                if conf > confidence:

                    if classNames[cls] == 'Quan':
                        color = (0,255,0)
                        id = 1
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Hung':
                        color = (0,255,0)
                        id = 2
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Thinh':
                        color = (0,255,0)
                        id = 3
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Hai':
                        color = (0,255,0)
                        id = 4
                        if count == 0:
                            count = 1
                    else:
                        color = (0,0,255)

                    # cvzone.cornerRect(img, (x1, y1, w, h), colorC=color, colorR=color)
                    # cvzone.putTextRect(img, f'{classNames[cls]}', (max(0, x1), max(35, y1)), scale=2,
                    #                     thickness=4, colorR=color, colorB=color)



        if count != 0:

            if count == 1:
                export_data(ref_export=db.reference(f'Employee/{id}'),
                            datetime_final_in_month=int(datetime.now().strftime('%d')),
                            total_attendance=db.reference(f"Employee/{id}/Total attendance in Month").get(),
                            first_day_in_month=1)

                ##### check to reset data ####
                reset_data(ref=db.reference('Employee'), datetime_final_in_month=int(datetime.now().strftime('%d')),
                           check_date_had=db.reference(f"Employee/{id}/Last attendance in").get(),
                           total_attendance=db.reference(f"Employee/{id}/Total attendance in Month").get())

                employeeInfo = db.reference(f'Employee/{id}').get()
                # print(employeeInfo)

                datetime_reset_in = db.reference(f'Employee/{id}/Last attendance in').get()
                datetime_reset_out = db.reference(f'Employee/{id}/Last attendance out').get()

                ### Update data ###
                ### IN ######
                # datetime1 = datetime.strptime(employeeInfo['Last attendance in'],
                #                              "%Y-%m-%d %H:%M:%S")  ## format for time
                # secondsElapsedIn = (datetime.now()-datetime1).total_seconds()
                # ### OUt ####
                # datetime2 = datetime.strptime(employeeInfo['Last attendance out'],
                #                              "%Y-%m-%d %H:%M:%S")
                # secondsElapsedOut = (datetime.now()-datetime2).total_seconds()

                # print(secondsElapsed)
                if selectINorOut == 1: ### IN ####

                    if datetime_reset_in == "":
                        ref = db.reference(f'Employee/{id}')
                        ref.child('Last attendance in').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        employeeInfo['Total attendance in Month'] += 1
                        num = employeeInfo['Total attendance in Month'] - 1
                        ref.child('Total attendance in Month').set(employeeInfo['Total attendance in Month'])
                        ref.child(f"List of Workday/{num}/in").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        selectINorOut = 0
                    else:
                        ### IN ######
                        datetime1 = datetime.strptime(employeeInfo['Last attendance in'],
                                                      "%Y-%m-%d %H:%M:%S")  ## format for time
                        secondsElapsedIn = (datetime.now() - datetime1).total_seconds()
                        if secondsElapsedIn > 36:
                            ref = db.reference(f'Employee/{id}')
                            employeeInfo['Total attendance in Month'] += 1
                            num = employeeInfo['Total attendance in Month'] - 1
                            ref.child('Total attendance in Month').set(employeeInfo['Total attendance in Month'])
                            ref.child('Last attendance in').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            ref.child(f"List of Workday/{num}/in").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            selectINorOut = 0
                        else:
                            indexImageMode = 3
                            selectINorOut = 0

                elif selectINorOut == 2: ## OUT ###

                    if datetime_reset_out == "":
                        ref = db.reference(f'Employee/{id}')
                        num = employeeInfo['Total attendance in Month'] - 1
                        ref.child('Last attendance out').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        ref.child(f"List of Workday/{num}/out").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        selectINorOut = 0
                    else:
                        datetime2 = datetime.strptime(employeeInfo['Last attendance out'],
                                                      "%Y-%m-%d %H:%M:%S")
                        secondsElapsedOut = (datetime.now() - datetime2).total_seconds()
                        if secondsElapsedOut > 36:
                            ref = db.reference(f'Employee/{id}')
                            num = employeeInfo['Total attendance in Month'] - 1
                            ref.child('Last attendance out').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            ref.child(f"List of Workday/{num}/out").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            selectINorOut = 0
                        else:
                            indexImageMode = 3
                            selectINorOut = 0

            if indexImageMode == 3:
                count +=1
                if count > 10:
                    indexImageMode = 0
                    count = 0


            if 1< indexImageMode <3:

                if 30< count < 40:
                    indexImageMode = 2

                if count <=30:
                    cv2.putText(imgBackground, str(employeeInfo['Total attendance in Month']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(employeeInfo['Position']), (1030, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(1), (1030, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(employeeInfo['Date of Birth']), (1115, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(employeeInfo['Starting year']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(employeeInfo['Address']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                    (w, h), _ = cv2.getTextSize(employeeInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(employeeInfo['Name']), (900 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)

                count +=1

                if count >=40:
                    count = 0
                    indexImageMode = 0
                    employeeInfo = []
    #########################################################
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print(fps)
    #print(selection)
    ### Display image background ###
    cv2.imshow('Image background',imgBackground)
    #cv2.imshow('Image',img)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cv2.destroyAllWindows()