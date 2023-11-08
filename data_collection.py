import cvzone
from cvzone.FaceDetectionModule import FaceDetector
import cv2
from time import time
##### Collect Face ##########

############################
classID = 1 # 0 is fake and 1 is real
offsetPercentagesW = 10
offsetPercentagesH = 20
confidence = 0.8
camWidth, camHeight = 640,480
save = True
blurThreshold = 35 # larger is more focus
outputFolderPath = 'D:/Attendance_system/Datasets/Data_Collect'
debug = False ### test to file the value for blurThreshold
############################

cap = cv2.VideoCapture(0)
cap.set(3,camWidth)
cap.set(4,camHeight)
detector = FaceDetector()

while True:
    success, img = cap.read()
    imgOut = img.copy()
    img, bboxs = detector.findFaces(img,draw=False)

    listBlur = [] ### True False values indicating if the faces are blur or not
    listInfo = [] ### The normalized values and the class name for the label txt file

    if bboxs:
        # bboxInfo - "id","bbox","score","center"
        for bbox in bboxs:
            x,y,w,h = bbox['bbox']
            score = bbox['score'][0]
            #print(x,y,w,h)
            #print(score)
            ####### Check the score (confidence value)  --------------
            if score > confidence:

                ######Adding an offset to the face Detected #####
                ### Edit the width of boundingbox ######
                offsetW = (offsetPercentagesW / 100)*w
                x = int(x - offsetW)
                w = int(w + offsetW * 2)
                ### Edit the height of boundingbox #####
                offsetW = (offsetPercentagesH / 100) * h
                y = int(y - offsetW * 3)
                h = int(h + offsetW * 3.5)

                #### Avoiding ( tránh ) value below 0 for boundingbox ##########
                if x < 0: x = 0
                if y < 0: y = 0
                if w < 0: w = 0
                if h < 0: h = 0

                ###### Find Blurriness of Face ####################
                imgface = img[y:y+h,x:x+w]
                ## y:y+h : it means height of image from y --> y+h
                ## x:x+h : it means width of image from x --> x+h
                cv2.imshow('Face',imgface)
                blurvalue = int(cv2.Laplacian(imgface, cv2.CV_64F).var()) ##get the value blur
                if blurvalue > blurThreshold:
                    listBlur.append(True)
                else:
                    listBlur.append(False)

                ###### Normalize the value 0--1 ##############
                imgH,imgW,_ = img.shape ### heigth,width,channel (here we don't care with channel
                x_center, y_center = x + w/2, y + h/2 ### center point
                #print(x_center,y_center)
                x_center_norm = round(x_center / imgW,6) ### lấy sau dấu phẩy 6 số
                y_center_norm = round(y_center / imgH,6)
                #print(x_center_norm,y_center_norm)
                w_norm, h_norm = round(w / imgH,6), round(h / imgH,6)
                #print(x_center_norm, y_center_norm,w_norm,h_norm)

                #### Avoiding ( tránh ) value below 0 for the normalized value ##########
                if x_center_norm > 1: x_center_norm = 1
                if y_center_norm > 1: y_center_norm = 1
                if w_norm > 1: w_norm = 1
                if h_norm > 1: h_norm = 1

                listInfo.append(f'{classID} {x_center_norm} {y_center_norm} {w_norm} {h_norm}\n')

                ###### Drawing ######################################
                # cv2.rectangle(imgOut,(x,y,w,h),(255,0,0),3)
                # cvzone.putTextRect(imgOut,f'Score : {int(score*100)}% Blur : {blurvalue}',(x,y-20),
                #                    scale=1.4, thickness=2)
                if debug:
                    cv2.rectangle(img, (x, y, w, h), (255, 0, 0), 3)
                    # cvzone.putTextRect(img, f'Score : {int(score * 100)}% Blur : {blurvalue}', (x, y - 20),
                    #                scale=1.4, thickness=2)

        ####### To Save ########################
        if save:
            if all(listBlur) and listBlur != []:
                #### Save IMAGE #################
                timeNow = time()
                timeNow = str(timeNow).split('.')
                timeNow = timeNow[0] + timeNow[1]
                #print(timeNow)
                cv2.imwrite(f'{outputFolderPath}/{timeNow}.jpg',img)

                ### Save lebel Text File #######
                for info in listInfo:
                    f = open(f"{outputFolderPath}/{timeNow}.txt", 'a')  ## 'a' : append (mode)
                    f.write(info)
                    f.close()

    cv2.imshow("Image", imgOut)
    if cv2.waitKey(1) & 0xff==ord('q'):
        break
cv2.destroyAllWindows()