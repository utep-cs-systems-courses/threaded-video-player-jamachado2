#!/usr/bin/env python3

import threading, cv2, time, base64
from threading import Thread, Semaphore
import numpy as np

semExtract   = Semaphore(10)   # Limit our queue to 10
semConvert   = Semaphore(10)   # Limit our queue to 10
semDisplay   = Semaphore()
mutExtract   = threading.Lock()
mutConvert   = threading.Lock()
queueExtract = []   # store our frames
queueConvert = []   # store our converted frames to gray

class extractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)

        #initialize frane count
        self.count = 0
        self.vidcap = cv2.VideoCapture(filename) # open video file
        self.maxFramesToLoad = 9999           
        self.maxQueue = 9999
        
    def run(self):
        global semExtract
        global queueExtract
        global mutExtract
        
        success, image = self.vidcap.read()  # read first iamge

        print(f'Reading frame {queueExtract} {success}')
        while success and len(queueExtract) <= self.maxQueue:
            # get a jpg encoded frame
            success, jpgImage = cv2.imencode('.jpg', image)

            #encode the frame as base 64 to make debugginf easier
            jpgAsText = base64.b64encode(jpgImage)

            #add frame to the queue
            semExtract.acquire()
            mutExtract.acquire()
            queueExtract.append(image)
            mutExtract.release()
            semExtract.release()

            success, image = self.vidcap.read()
            print(f'Reading frame {self.count} {success}')
            self.count += 1

            # stop on the last element in the queue
            if self.count == self.maxFramesToLoad:
                semExtract.acquire()
                mutExtract.acquire()
                queueExtract.append(-1)
                mutExtract.release()
                semaphore.release()

        print('Frame extraction complete.')

class convertToGrayScale(Thread):
    def __init__(self):
        Thread.__init__(self)
        #initialize frame count
        self.count = 0
        self.maxQueue = 9999

    def run(self):
        global queueExtract
        global queueConvert
        global semConvert
        global mutConvert

        while True:
            if queueExtract and len(queueConvert) <= self.maxQueue:
                semConvert.acquire()
                mutConvert.acquire()
                frame = queueExtract.pop(0)
                mutConvert.release()
                semConvert.release()

                print(f'Converting Frame {self.count}')

                # convert the image to grayscale
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                semConvert.acquire()
                mutConvert.acquire()
                queueConvert.append(grayscaleFrame)
                mutConvert.release()
                semConvert.release()
                self.count += 1
                
        print("Converting to gray scale complete.")
            
# Display Class here
class displayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        #initialize frame count
        self.count = 0
        self.delay = 42
        
    def run(self):
         global queueConvert
         global semDisplay
         
         while True:
             # go through each frame
             if queueConvert:
                 # get the next frame
                 semDisplay.acquire()
                 frame = queueConvert.pop(0)
                 semDisplay.release()
                 
                 print(f'Displaying Frame {self.count}')
                 
                 #display the image in a window called "video" and wait 42
                 #before displaying the next frame
                 cv2.imshow('Video', frame)
                 if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                     break

                 self.count +=1
                 
         print("Display frame complete.")
         #destory video screen
         cv2.destroyAllWindows()
       
        
filename = 'clip.mp4'
# run our threads
extractFrames = extractFrames()
extractFrames.start()

convertToGrayScale  = convertToGrayScale()
convertToGrayScale.start()

displayFrames = displayFrames()
displayFrames.start()
