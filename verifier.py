import threading
import time
import os
from job import *
class Verifier(threading.Thread):
    threads = []
    verified = 0
    notExistingHosts = 0
    existingHosts = 0
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

                        lookup = os.popen('nslookup -q=mx ' + job.host).readlines()

                        lookup = [x.rstrip() for x in lookup if 'exchanger' in x]

                        mxList = []

                        for i in lookup:
                            line = i.split(',')
                            mxList.append((line[0].split('=')[-1].strip(), line[1].split('=')[-1].strip()))

                        if mxList:
                            Verifier.existingHosts += 1
                        else:
                            Verifier.notExistingHosts += 1

                        print job.host, sorted(mxList)
                        self.master.lock.release()

                        if not self.master.hdButtonTick.get():
                            for i in job.accounts:
                                email = i + '@' + job.host
                                time.sleep(0.2)
                                self.master.lock.acquire()
                                self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + email, 'OK'))
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
                            self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + email, 'OK'))
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
                    print Verifier.existingHosts
                    print Verifier.notExistingHosts
