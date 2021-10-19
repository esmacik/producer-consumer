from threading import Lock, Semaphore

# My implementation of a tread safe queue that utilizes a mutex and two semaphores.
# Mutex:  used to prevent another thread from accessing queue while something is being enqueued or dequeued
# Semaphore: used to keep track of how many empty and full spaces there are, and if a thread is able to enqueue or
# dequeue

class Queue:
    def __init__(self, size):
        self.list = []    # Use a list because it is not thread safe by default, so we may implement it
        self.emptySemaphore = Semaphore(size)    # There are size empty spaces when the queue is constructed
        self.fullSemaphore = Semaphore(0)    # There are 0 full spaces when the queue is constructed
        self.mutex = Lock()

    def enqueue(self, item):
        self.emptySemaphore.acquire()    # Ask the semaphore if there is an empty space. If not, wait for one
        self.mutex.acquire()    # Lock down queue so no one else messes up my work
        self.list.append(item)
        self.mutex.release()    # My critical work is done, everyone carry on
        self.fullSemaphore.release()    # Signal to consumer that there is in fact something to take off this queue

    def dequeue(self):
        self.fullSemaphore.acquire()    # Ask the semaphore if there is anything to grab. If not, wait for something
        self.mutex.acquire()    # Lock down queue so no one else messes up my work
        dequeuedItem = self.list.pop(0)
        self.mutex.release()    # My critical work is done, everyone carry on
        self.emptySemaphore.release()    # Signal to producer that there is in fact space to insert into this queue
        return dequeuedItem
