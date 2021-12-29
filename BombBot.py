from cv2 import cv2
import numpy as np
import mss
import pyautogui
import time
import datetime

reenterDelay = 60
goToWorkDelay = 60 * 20
movementDuration = .1
waitNextFrameDelay = .1
imageDict = {
    "Return" : {"path":"./Images/BackArrow.png", "threshold": .95},
    "Heroes" : {"path":"./Images/Heroes.png", "threshold": .9},
    "Work" : {"path":"./Images/Work.png", "threshold": .94},
    "Rest" : {"path":"./Images/Rest.png", "threshold": .93},
    "X" : {"path":"./Images/X.png", "threshold": .9},
    "TreasureHunt" : {"path":"./Images/TreasureHunt.png", "threshold": .9},
    "NewMap" : {"path":"./Images/NewMap.png", "threshold": .9},
    }

def LogWithTime(time, message):
    date = datetime.datetime.fromtimestamp(time)
    format = "[{}] {}"
    print(format.format(date, message))
def DebugCircle(position):
    frame = ScreenShot()
    image = np.ascontiguousarray(frame, dtype=np.uint8)
    cv2.circle(image, position , 10, (0, 0, 255))
    cv2.imshow('title', image)
    cv2.waitKey(0)

def ScreenShot():
     with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def GetImage(imageName):
    path = imageDict[imageName]["path"]
    image = cv2.imread(path)
    return image

def MatchTemplate(template, frame, threshold):
    result = cv2.matchTemplate(frame,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    templateWidht = template.shape[1]
    templateHeight = template.shape[0]
    return max_loc[0] + int(templateWidht/2) , max_loc[1] + int(templateHeight/2)

def FindImage(imageName, timeout = 3, logErrorWhenNotFound = True):
    start = time.time()
    while(time.time() <= start + timeout):
        time.sleep(waitNextFrameDelay)
        frame = ScreenShot()
        threshold = imageDict[imageName]["threshold"]
        position = MatchTemplate(GetImage(imageName), frame, threshold)
        if(position is not None):
            return position
    if (logErrorWhenNotFound):
        print("image '" + imageName + "' not found")
    return None

def ClickAt(position):
    if(position is not None):
        pyautogui.moveTo(position[0], position[1], movementDuration)
        pyautogui.click()

def WorkAllRoutine():
    ClickAt(FindImage("Return"))
    position = FindImage("Heroes")
    if(position is None):
        return

    ClickAt(position)
    FindImage("X", timeout = 5) # wait for the heroes tab to load, timeout in 5 seconds
    time.sleep(1)

    # Scroll to the end of the heroes list
    positionToScroll = (position[0] - 700, position[1] - 300)
    for i in range(0,3):
        pyautogui.moveTo(positionToScroll[0], positionToScroll[1], movementDuration)
        pyautogui.drag(0, -200, .5)

    time.sleep(.5)
    # Click all work buttons
    for i in range(0,20):
        position = FindImage("Work", timeout = .5, logErrorWhenNotFound = False)
        if(position is None):
            break
        ClickAt(position)

    ClickAt(FindImage("X"))
    ClickAt(FindImage("TreasureHunt"))

def ReenterTreasureHunt():
    ClickAt(FindImage("Return"))
    ClickAt(FindImage("TreasureHunt"))

def Main():
    print("initiating bot in 5 seconds...")
    time.sleep(5)
    lastWorkUpdate = 0
    lastReenter = 0
    while(True):
        now = time.time()

        # check for new map
        position = FindImage("NewMap", logErrorWhenNotFound = False)
        if(position is not None):
            LogWithTime(now, "Entering new map...")
            ClickAt(position)

        if(now - lastWorkUpdate > goToWorkDelay):
            LogWithTime(now, "Executing work routine...")
            lastWorkUpdate = now
            lastReenter = now
            WorkAllRoutine()
        elif(now - lastReenter > reenterDelay):
            lastReenter = now
            ReenterTreasureHunt()

        time.sleep(1)

Main()