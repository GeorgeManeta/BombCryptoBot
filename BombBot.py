from cv2 import cv2
import numpy as np
import mss
import pyautogui
import time

movementDuration = .2
waitNextFrameDelay = .1
imageDict = {
    "Return" : {"path":"./Images/BackArrow.png", "threshold": .95},
    "Heroes" : {"path":"./Images/Heroes.png", "threshold": .95},
    "Work" : {"path":"./Images/Work.png", "threshold": .94},
    "Rest" : {"path":"./Images/Rest.png", "threshold": .93},
    "X" : {"path":"./Images/X.png", "threshold": .9},
    "TreasureHunt" : {"path":"./Images/TreasureHunt.png", "threshold": .9},
    "NewMap" : {"path":"./Images/NewMap.png", "threshold": .9},
    }

def GetImage(imageName):
    path = imageDict[imageName]["path"]
    image = cv2.imread(path)
    return image

def ScreenShot():
     with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def Find(template, frame, threshold):
    result = cv2.matchTemplate(frame,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    templateWidht = template.shape[1]
    templateHeight = template.shape[0]
    return max_loc[0] + int(templateWidht/2) , max_loc[1] + int(templateHeight/2)
    
def MoveMouseTo(position):
    if(position == None):
        print("trying to move to None position")
        return;
    pyautogui.moveTo(position[0], position[1], movementDuration)

def FindImageAndClick(imageName):
    frame = ScreenShot()
    threshold = imageDict[imageName]["threshold"]
    position = Find(GetImage(imageName), frame, threshold)
    if(position is not None):
        MoveMouseTo(position)
        pyautogui.click()
        time.sleep(waitNextFrameDelay)
    return position

def DebugCircle(position):
    frame = ScreenShot()
    image = np.ascontiguousarray(frame, dtype=np.uint8)
    cv2.circle(image, position , 10, (0, 0, 255))
    cv2.imshow('title', image)
    cv2.waitKey(0)

def WorkAllRoutine():
    FindImageAndClick("Return")
    position = FindImageAndClick("Heroes")
    if(position is None):
        print("couldn't find 'heroes' button")
        return
    time.sleep(.5)

    # Scroll to the end of the heroes list
    positionToScroll = (position[0] - 700, position[1] - 300)
    for i in range(0,3):
        MoveMouseTo(positionToScroll)
        pyautogui.drag(0, -200, movementDuration)

    time.sleep(waitNextFrameDelay)
    for i in range(0,15):
        position = FindImageAndClick("Work")
        if(position is None):
            break

    FindImageAndClick("X")
    time.sleep(.5)
    FindImageAndClick("TreasureHunt")

def Main():
    time.sleep(5)
    lastWorkUpdate = 0
    secondsNeededToWorkRoutine = 10*60
    while(True):
        FindImageAndClick("NewMap")
        time.sleep(1);
        now = time.time()
        if(now - lastWorkUpdate > secondsNeededToWorkRoutine):
            lastWorkUpdate = now
            print("executing work routine")
            WorkAllRoutine()

Main()