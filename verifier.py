import threading
import time
from job import *
class Verifier(threading.Thread):
    threads = []
    verified = 0
    def __init__(self, id, master):
        threading.Thread.__init__(self)
        self.master = master
        self.id = id
        self.active = False
        self.myJob = None
        self.quit = False
        Verifier.threads.append(self)

    def getMXRecords(self):
        pass

    def connect(self):
        pass

    def run(self):
        while True:
            while self.active and self.master.taskActive:
                if Job.jobsList:
                    job = Job.jobsList.pop(0)
                    if not self.master.hdButtonTick.get():
                        for i in job.accounts:
                            time.sleep(0.05)
                            self.master.lock.acquire()
                            self.master.verifierLog.append(('THREAD-' + str(self.id) + ' ' + i + '@' + job.host, 'OK'))
                            Verifier.verified += 1
                            self.master.lock.release()

                    for i in job.custom:
                        time.sleep(0.05)
                        self.master.lock.acquire()
                        self.master.verifierLog.append(('THREAD-' + str(self.id) + ' ' + i + '@' + job.host, 'OK'))
                        Verifier.verified += 1
                        self.master.lock.release()
                else:
                    self.active = False

