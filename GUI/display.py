################# Import Libraries ################
import os
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import cvzone
from ultralytics import YOLO
import time
from reset_date import reset_data
from datetime import datetime
from export_Data import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import json
####################################################

#########---------------------------------------------- For GG FireBase ---------------------------------------------------#########
cred = credentials.Certificate("/home/pi/Desktop/Attendance_system/attendance-system-f3c35-firebase-adminsdk-s7c8b-2b1990099a.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://attendance-system-f3c35-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'attendance-system-f3c35.appspot.com'
})
bucket = storage.bucket()
#----------------------------------------------------------------------------------------------------------------------------------#

#####------------- Webcam -------------#####
cap = cv2.VideoCapture(0)
cap.set(3,640) ### width of camera
cap.set(4,480) ### height of camera
cap.set(10,150) ### set brightness of camera
#------------------------------------------#

################ Hand Detection #########################
# ---- maxHands : số lượng bàn tay ---- #
# ---- detectionCon : độ tin cậy ---- #
hand_detector = HandDetector(maxHands=1,detectionCon=0.7)
#-------------------------------------------------------#

########################## Image Background #############################################
imgBackground = cv2.imread('/home/pi/Desktop/Attendance_system/Resources/background.png')
#---------------------------------------------------------------------------------------#

###### Import a list contain the value of each images for attendance system #######
folderPathModes = '/home/pi/Desktop/Attendance_system/Resources/Modes'
listPathModes = os.listdir(folderPathModes)
#print(listPathModes) ## test để xem listPathModes có gì
listImageModes = []
for imagePathModes in listPathModes:
    listImageModes.append(cv2.imread(os.path.join(folderPathModes,imagePathModes)))
# print(listImageModes)
#---------------------------------------------------------------------------------#

################--------- Load Model trained ---------------##################
model = YOLO('/home/pi/Desktop/Attendance_system/models/yolov8n_imgsz_226.pt')
classNames = ['Fake', 'Quan', 'Hung']
#----------------------------------------------------------------------------#

############ Một vài thông số ##############
counter = 0
selectionSpeed = 20
selection = -1
modePositions = [(1016,238),(1016,438)]
colorMode = [(0,255,0), (0,0,255)]
indexImageMode = 0
# pauseCounter = 0
confidence = 0.7
id = 0
count = 0
selectINorOut = 0
prev_frame_time = 0
new_frame_time = 0
employeeInfo = []
imgEmployee = []
#------------------------------------------#

############# ------------------------ RUN APP AND PROJECT ------------------------------------- #################
while True:

    new_frame_time = time.time() ## để tính FPS

    success, img = cap.read() ## lấy giá trị từ camera
    ###################### MODEL #######################
    results = model(img, stream=True, verbose=False) ## lấy dữ liệu từ model YOLO sau khi đã dự đoán

    ################## Display the Webcam ################
    # cv2.imshow('camera',img)
    imgBackground[160:160 + 480, 53:53 + 640] = img ## hiển thị camera trên khung image Background chính

    ################## Display the image Mode #############################
    imgBackground[44:44+633, 808:808+414] = listImageModes[indexImageMode] # Hiển thị image các mode trên khung image Background chính

    ### Process first mode ######
    if indexImageMode == 0 :

        ################## Detect Hand #####################
        hands, img = hand_detector.findHands(img) ## get giá trị bàn tay
        # print(hands)

        if hands: ### Check phát hiện bàn tay
            ####### Lấy dữ liệu từ bàn tay ########
            hand1 = hands[0]
            # print(hand1)
            finger1 = hand_detector.fingersUp(hand1)
            # print(finger1)

            ####### Kiểm tra dơ mấy ngón tay lên ####
            if finger1 == [0,1,0,0,0]: # Dơ 1 ngón
                if selection != 1:
                    counter = 1
                selection = 1
            elif finger1 == [0,1,1,0,0]: # dơ 2 ngón
                if selection != 2:
                    counter = 1
                selection = 2
            else :
                selection = -1
                counter = 0
            ##########################################

            ########### Tạo một khoảng time để xđ lựa chọn ######################
            if counter > 0 :
                counter += 1
                #print(counter)
                #### create a ellipse for selection ####
                cv2.ellipse(imgBackground, modePositions[selection-1], (77,77),0,0,
                            counter*selectionSpeed, colorMode[selection-1],15) ### Tạo một vòng lựa chọn cho chế độ điểm danh IN or OUT
                selectINorOut = selection ## gán value lựa chọn điểm danh IN OR OUT
                if counter * selectionSpeed > 360: ## Check sau khi đã hoàn thiện vòng tròn
                    counter = 1
                    selection = -1
                    indexImageMode +=1
                    # pauseCounter = 1
            ######################################################################

    # if pauseCounter > 0:
    #     pauseCounter +=1
    #     if pauseCounter > 20:
    #         pauseCounter = 0

    ################### Next mode ####################
    else : #MODE 1

        ########## Get the value from model YOLO trained #####################
        for r in results:
            boxes = r.boxes
            for box in boxes:
                ### Khong can quan tam boundingbox ###
                ### bounding box ####
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                w, h = x2 - x1, y2 - y1 ##

                ### confidence ###### gia tri tin cay
                conf = math.ceil((box.conf[0] * 100)) / 100
                # print(conf)

                ### class Name ######
                cls = int(box.cls[0])

                #############################################################
                if conf > confidence: # > 0.7

                    if classNames[cls] == 'Quan': ## Neu la 'Quan'
                        color = (0,255,0)
                        id = 1
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Hung': ## Neu la 'Hung'
                        color = (0,255,0)
                        id = 2
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Thinh': ## Neu la 'Thinh'
                        color = (0,255,0)
                        id = 3
                        if count == 0:
                            count = 1
                    elif classNames[cls] == 'Hai': ## Neu la 'Hai'
                        color = (0,255,0)
                        id = 4
                        if count == 0:
                            count = 1
                    else: ## Neu la 'Fake'
                        color = (0,0,255)

                    # cvzone.cornerRect(img, (x1, y1, w, h), colorC=color, colorR=color)
                    # cvzone.putTextRect(img, f'{classNames[cls]}', (max(0, x1), max(35, y1)), scale=2,
                    #                     thickness=4, colorR=color, colorB=color)
                ##################################################################

        if count != 0:

            if count == 1:

                if selectINorOut == 1: ### IN ####

                    ####################---------------- Export_Data------------###################################
                    export_data(datetime_final_in_month=int(datetime.now().strftime('%d')),
                                first_day_in_month=1, month_now_export=int(datetime.now().strftime('%m')),
                                data=db.reference(f'Employee/{id}').get(),
                                file_name=db.reference(f"Employee/{id}/Name").get())

                    ###################----------------- Reset data-------------#######################################
                    reset_data(ref_rs= db.reference(f"Employee/{id}"), datetime_final_in_month=int(datetime.now().strftime('%d')),
                                month_now=int(datetime.now().strftime('%m')))

                    ###########################################################################
                    employeeInfo = db.reference(f'Employee/{id}').get()
                    datetime_reset_in = db.reference(f'Employee/{id}/Last attendance in').get()
                    ###########################################################################

                    if datetime_reset_in == "": #### IN ##### ---- Check nếu giá trị đầu vào trống
                        ref = db.reference(f'Employee/{id}')
                        ref.child('Last attendance in').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #-- Update time điểm danh lúc vào
                        employeeInfo['Total attendance in Month'] += 1 # -- Tăng tổng số lần điểm danh trong tháng sau khi điểm danh lúc vào
                        num = employeeInfo['Total attendance in Month'] - 1
                        ref.child('Total attendance in Month').set(employeeInfo['Total attendance in Month']) # -- Update tổng số lần điểm danh trong tháng
                        ref.child(f"List of Workday/{num}/in").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # -- Update time điểm danh lúc vào vào trong list work day tương ứng
                        selectINorOut = 0
                    else:
                        ##### IN ######
                        datetime1 = datetime.strptime(employeeInfo['Last attendance in'],
                                                        "%Y-%m-%d %H:%M:%S")  ## format for time # --- Lấy giá trị điểm danh lúc vào từ FireBase
                        secondsElapsedIn = (datetime.now() - datetime1).total_seconds() # -- Tính toán thời gian kể từ khi lúc điểm danh vào cho đến nay bằng giây
                        if secondsElapsedIn > 30:#57600: ### 16 tiếng
                            ref = db.reference(f'Employee/{id}')
                            employeeInfo['Total attendance in Month'] += 1
                            num = employeeInfo['Total attendance in Month'] - 1
                            ref.child('Total attendance in Month').set(employeeInfo['Total attendance in Month'])
                            ref.child('Last attendance in').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            ref.child(f"List of Workday/{num}/in").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            selectINorOut = 0
                        else: ### nếu chưa tới 16 tiếng
                            indexImageMode = 3 ## Chuyển qua chế độ mode số 3 (Already Marked)
                            selectINorOut = 0
                            count += 1

                elif selectINorOut == 2: ## OUT ###
                    employeeInfo = db.reference(f'Employee/{id}').get()
                    datetime_reset_out = db.reference(f'Employee/{id}/Last attendance out').get()
                    if datetime_reset_out == "": # -- Kiểm tra thời gian lúc check out xem có trống hay không
                        ref = db.reference(f'Employee/{id}')
                        num = employeeInfo['Total attendance in Month'] - 1
                        ref.child('Last attendance out').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # -- Update thời gian lúc ra
                        ref.child(f"List of Workday/{num}/out").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # -- Update thời gian lúc ra vào list of worday tương ứng
                        selectINorOut = 0
                    else:
                        ## OUT ##
                        datetime2 = datetime.strptime(employeeInfo['Last attendance out'],
                                                        "%Y-%m-%d %H:%M:%S") # -- Lấy giá trị thời gian lúc ra từ FireBase
                        secondsElapsedOut = (datetime.now() - datetime2).total_seconds() # -- Tính toàn thời gian lúc ra trước đó đến thời gian lúc ra hiện tại bằng giây
                        if secondsElapsedOut > 30:#54000: ### 15 tiếng
                            ref = db.reference(f'Employee/{id}')
                            num = employeeInfo['Total attendance in Month'] - 1
                            ref.child('Last attendance out').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            ref.child(f"List of Workday/{num}/out").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            selectINorOut = 0
                        else:
                            indexImageMode = 3 ## Chuyển qua chế độ mode số 3 (Already Marked)
                            selectINorOut = 0
                            count += 1

            if indexImageMode != 3:

                if 10 <= count <= 15:
                    indexImageMode = 2 ## Chế độ mode số 2 (Marked) Điểm danh thành công

                if count < 10:
                    ########### Lấy ảnh từ storage của GG FireBase ###################
                    blob = bucket.get_blob(f'Images/{id}.jpg')
                    array = np.frombuffer(blob.download_as_string(),np.uint8)
                    imgEmployee = cv2.imdecode(array,cv2.COLOR_BGR2RGB)

                    ########### Hiển thị các thông tin về nhân viên và ảnh lên Image Background #########
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
                    imgBackground[175:175+216,909:909+216] = imgEmployee
                    #-------------------------------------------------------------------------------------#

                count +=1

                if count > 15:
                    count = 0
                    indexImageMode = 0
                    employeeInfo = []
                    imgEmployee = []
                    id=0

            ####### MODE Already Marked ########
            if indexImageMode == 3:
                count +=1
                if count >= 12:
                    indexImageMode = 0 # chuyển về chế độ mode ban đầu
                    count = 0
                    employeeInfo=[]
                    imgEmployee = []
                    id=0
            ####################################

    #######---------------Calculate FPS-------------#########
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print(fps)
    #-------------------------------------------------------#

    ###-------------------- Display image background ------------------------###
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow('window',imgBackground)
    #--------------------------------------------------------------------------#

    ###-- Turn off Image of Project --###
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    #-----------------------------------#
cv2.destroyAllWindows()