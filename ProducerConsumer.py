import cv2
import threading
from MyQueue import Queue
import numpy as np

# IMPORTANT NOTE: macOS does not allow the creation of GUI elements on anything but the main thread, so I am treating
# the main thread as the third thread that is responsible for displaying the frames. If I try to make a third thread, I
# get a horrible error that says the following, and nothing runs:
# "WARNING: NSWindow drag regions should only be invalidated on the Main Thread! This will throw an exception in the
# future."


def extractFrames(fileName, outputBuffer):
    count = 0    # Initialize frame count
    vidcap = cv2.VideoCapture(fileName)    # open video file
    success, image = vidcap.read()    # read first image
    print("Reading frame {} {} ".format(count, success))
    while success:
        success, jpgImage = cv2.imencode('.jpg', image)    # get a jpg encoded frame
        outputBuffer.enqueue(jpgImage)    # add the frame to the buffer

        success, image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1
    outputBuffer.enqueue(None)
    print("\tFinished extracting frames!")


def convertToGrayscale(inputBuffer, outputBuffer):
    # initialize frame count
    count = 0
    while True:
        jpgImage = inputBuffer.dequeue()    # Grab a frame from the input buffer
        if jpgImage is None:    # There is nothing left to grab, so we are done
            print("\tFinished converting to Grayscale!")
            outputBuffer.enqueue(None)    # Signal to the buffer and other consumer that we are done
            return

        print("Converting frame {}".format(count))
        jpgImage = np.asarray(bytearray(jpgImage), dtype=np.uint8)    # convert the raw frame to a numpy array
        img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)    # get a jpg encoded frame
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # convert the image to grayscale
        success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)    # create a jpg encoding of this frame
        count += 1
        outputBuffer.enqueue(jpgImage)    # add to output buffer


def displayFrames(inputBuffer):
    count = 0    # initialize frame count
    while True:    # go through each frame in the buffer until the buffer is empty
        jpgImage = inputBuffer.dequeue()    # get the next frame
        if jpgImage is None:    # There is nothing left to grab, so we are done
            print("\tFinished displaying all frames")
            cv2.destroyAllWindows()    # cleanup the windows
            return

        jpgImage = np.asarray(bytearray(jpgImage), dtype=np.uint8)    # convert the raw frame to a numpy array
        img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)    # get a jpg encoded frame
        print("Displaying frame {}".format(count))

        # display the image in a window called "video" and wait 42ms before displaying the next frame
        cv2.imshow("Video", img)

        # determine the amount of time to wait, also make sure we don't go into negative time
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        count += 1


filename = 'clip.mp4'    # filename of clip to load

# My implementation of a thread-safe queue
queue1 = Queue(10)    # First producer consumer queue, bounded at 10 frames
queue2 = Queue(10)    # Second producer consumer queue, bounded at 10 frames
print("\tQueues created")

t1 = threading.Thread(target=extractFrames, args=(filename, queue1))
t2 = threading.Thread(target=convertToGrayscale, args=(queue1, queue2))
#t3 = threading.Thread(target=displayFrames, args=(queue2, ))
print("\tThreads created")

t1.start()
t2.start()
displayFrames(queue2)
# t3.start()

# IMPORTANT NOTE: macOS does not allow the creation of GUI elements on anything but the main thread, so I am treating
# the main thread as the third thread that is responsible for displaying the frames. If I try to make a third thread, I
# get a horrible error that says the following, and nothing runs:
# "WARNING: NSWindow drag regions should only be invalidated on the Main Thread! This will throw an exception in the
# future."
