#! /usr/bin/python3

import threading, cv2, time, base64
from threading import Thread, Semaphore

class Queue():
    def __init__(self):
        self.queue = []
        self.full = Semaphore(0)
        self.empty = Semaphore(10) # limits queue to 10
        self.mutex = threading.Lock()
        
    def put(self, frame):
        self.empty.acquire()
        self.mutex.acquire()
        self.queue.append(frame)
        self.mutex.release()
        self.full.release()
    
    def get(self):
        self.full.acquire()
        self.mutex.acquire()
        frame = self.queue.pop(0)
        self.mutex.release()
        self.empty.release()
        return frame
    
    
queueExtract     = Queue()
queueConvert     = Queue()


class extractFrames(Thread):
    def __init__(self):  
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture(filename)
        # get total frames of the video
        self.maxFramesToLoad = 9999
        # initialize the frame count
        self.count = 0
        
    def run(self):
        success, image = self.videoCapture.read()

        while success: 
            # get the frame
            queueExtract.put(image)
          
            success, image = self.videoCapture.read()
    
            print(f'Reading frame {self.count}')
            self.count += 1

            # check forthe last element 
            if self.count == self.maxFramesToLoad:
                queueExtract.put(-1)
                break  
                
        print('Frame extraction complete')
            
class convertToGrayScale(Thread):
        def __init__(self):
            Thread.__init__(self)
            # initialize the frame count 
            self.count = 0
            
        def run(self):
           
            while True:
                # get a frame from the first queue
                frame = queueExtract.get()
               
                # converts image to grayscale
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                queueConvert.put(grayscaleFrame)
                
                print(f'Converting Frame {self.count}')
                self.count += 1
                
            print('Frame convertion complete')

class displayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        # delay of 42 ms
        self.delay = 42
        self.count = 0

    def run(self):

        while True:
            # get a grayscale frame
            frame = queueConvert.get()

            #display the image in a window called "video" and wait 42
            #before displaying the next frame
            cv2.imshow('Video', frame)
            if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                break
            self.count += 1
            
            print(f'Displaying Frame {self.count}')

                               
        #destory video screen
        cv2.destroyAllWindows()
        
        # signal that this thread has ended his work    
        print('Frame display complete')

filename = 'clip.mp4'
extractFrames = extractFrames()
extractFrames.start()

convertToGrayScale = convertToGrayScale()
convertToGrayScale.start()

displayFrames = displayFrames()
displayFrames.start()
