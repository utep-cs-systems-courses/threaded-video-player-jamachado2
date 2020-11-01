#!/usr/bin/env python3

import threading, cv2, time, base64
from threading import Thread, Semaphore
import numpy as np

global semaphore, queueExtract, queueConvert
semaphore = Semaphore()
queueExtract = []
queueConvert = []

class extractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)

        #initialize frane count
        self.count = 0
        self.vidcap = cv2.VideoCapture(filename) # open video file
        self.maxFramesToLoad = 9999           
        self.maxQueue = 9999
        
    def run(self):
        global semaphore
        global queueExtract
        
        success, image = self.vidcap.read()  # read first iamge

        print(f'Reading frame {queueExtract} {success}')
        while success and len(queueExtract) <= self.maxQueue:
            # get a jpg encoded frame
            success, jpgImage = cv2.imencode('.jpg', image)

            #encode the frame as base 64 to make debugginf easier
            jpgAsText = base64.b64encode(jpgImage)

            #add frame to the queue
            semaphore.acquire()
            queueExtract.append(image)
            #semaphore.release()

            success, image = self.vidcap.read()
            print(f'Reading frame {self.count} {success}')
            self.count += 1
            semaphore.release()

            # stop on the last element in the queue
            if self.count == self.maxFramesToLoad:
                semaphore.acquire()
                queueExtract.append(-1)
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
        global semaphore

        while True:
            if queueExtract and len(queueConvert) <= self.maxQueue:
                semaphore.acquire()
                frame = queueExtract.pop(0)
                semaphore.release()

                print(f'Converting Frame {self.count}')

                # convert the image to grayscale
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # add the converted frame into the queueConvert
                semaphore.acquire()
                queueConvert.append(grayscaleFrame)
                semaphore.release()
                
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
         global semaphore

         while True:
             # go through each frame
             if queueConvert:
                 # get the next frame
                 semaphore.acquire()
                 frame = queueConvert.pop(0)
                 semaphore.release()
                 
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
extractFrames = extractFrames()
extractFrames.start()

convertToGrayScale  = convertToGrayScale()
convertToGrayScale.start()

displayFrames = displayFrames()
displayFrames.start()

