import os
import random
import shutil
from itertools import islice

classes = ['Fake', 'Quan', 'Hung']
#### Path of output for Folder #########
outputFolderPath = 'D:/Attendance_system/Datasets/SplitData'
inputFoderPath = 'D:/Attendance_system/Datasets/all'
splitRatio = {"train":0.7,"val":0.2,"test":0.1}
#### Check directory exist or not ? ####
try:
    shutil.rmtree(outputFolderPath)
    #print("Remove Directory")
except OSError as e:
    os.mkdir(outputFolderPath) ## create directory

#### Create to Directories for YOLO ############
os.makedirs(f"{outputFolderPath}/train/images",exist_ok=True)
os.makedirs(f"{outputFolderPath}/train/labels",exist_ok=True)
os.makedirs(f"{outputFolderPath}/val/images",exist_ok=True)
os.makedirs(f"{outputFolderPath}/val/labels",exist_ok=True)
os.makedirs(f"{outputFolderPath}/test/images",exist_ok=True)
os.makedirs(f"{outputFolderPath}/test/labels",exist_ok=True)

#### Get the only one value of name for file img and txt #################
listNames = os.listdir(inputFoderPath)
#print(listNames)
#print(len(listNames))
uniqueNames = [] ### Create a list to store the name of file img and txt
'''
    Because Name of file img and txt have the same so we need only 1 for them.
    So, we use split for name file to get the Name.
    Then, we use set() to collect only one value for Name.
'''
for name in listNames:
    uniqueNames.append(name.split('.')[0]) ### split the name of file img and txt
uniqueNames = list(set(uniqueNames)) ### set one value
#print(len(uniqueNames))

#### Shuffle ###########################
random.shuffle(uniqueNames)
#print(uniqueNames)

#### Find the number of images for each folder ###############
lenData = len(uniqueNames)
lenTrain = int(lenData * splitRatio['train'])
lenVal = int(lenData * splitRatio['val'])
lenTest = int(lenData * splitRatio['test'])
print(f'Total Images : {lenData} \nSplit: {lenTrain} {lenVal} {lenTest}')

#### Addition the image for Trainning #######################
'''
    If u want to add the image for datasets,
    u can add them into train folder
'''
if lenData != lenTrain+lenVal+lenVal:
    remaining = lenData-(lenTrain+lenVal+lenVal)
    lenTrain += remaining
#print(f'Total Images : {lenData} \nSplit: {lenTrain} {lenVal} {lenTest}')

#### Split real the list Image #############################
lengthToSplit = [lenTrain, lenVal, lenTest]
Input = iter(uniqueNames)
Output = [list(islice(Input,elem)) for elem in lengthToSplit]
print(f'Total Images : {lenData} \nSplit: {len(Output[0])} {len(Output[1])} {len(Output[2])}')
#print(Output)

#### Copy the file to train, test, val folder ##############
sequence = ['train', 'val', 'test']
for i,out in enumerate(Output):
    for filename in out:
        shutil.copy(f'{inputFoderPath}/{filename}.jpg',f'{outputFolderPath}/{sequence[i]}/images/{filename}.jpg')
        shutil.copy(f'{inputFoderPath}/{filename}.txt',f'{outputFolderPath}/{sequence[i]}/labels/{filename}.txt')

print("Split process completed ....")

#### Create a Data Yaml ####################################
dataYaml = f'path: ../Data\n\
train: ../train/images\n\
val: ../val/images\n\
test: ../test/images\n\
\n\
nc: {len(classes)}\n\
names: {classes}'

f = open(f"{outputFolderPath}/data.yaml", 'a')  ## 'a' : append (mode)
f.write(dataYaml)
f.close()

print('Data.yaml file Created ....')