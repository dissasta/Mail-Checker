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
            while self.active:
                if self.master.taskActive:
                    self.master.lock.acquire()
                    if Job.jobsList:
                        job = Job.jobsList.pop(0)
                        self.master.lock.release()

                        if not self.master.hdButtonTick.get():
                            for i in job.accounts:
                                email = i + '@' + job.host
                                time.sleep(0.2)
                                self.master.lock.acquire()
                                self.master.verifierLog.append(('TH-' + str(self.id) + ' ' + email, 'OK'))
                                if Verifier.verified % 20 == 0:
                                    Job.jobsResultsMainFailed.append(email)
                                else:
                                    Job.jobsResultsMain.append(email)
                                Verifier.verified += 1
                                self.master.lock.release()

                        for i in job.custom:
                            email = i + '@' + job.host
                            time.sleep(0.2)
                            self.master.lock.acquire()
                            self.master.verifierLog.append(('TH-' + str(self.id) + ' ' + email, 'OK'))
                            if Verifier.verified % 500:
                                Job.jobsResultsCustomFailed.append(email)
                            else:
                                Job.jobsResultsCustom.append(email)
                            Verifier.verified += 1
                            self.master.lock.release()
                    else:
                        self.master.lock.release()
                        self.active = False
                else:
                    self.active = False
