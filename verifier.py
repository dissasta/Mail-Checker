class Verifier(object):
    active = []
    threads = []
    def __init__(self):
        self.id = self.getId()
        self.active = False
        self.myJob = None
        self.quit = False
        Verifier.threads.append(self)

    def getMXRecords(self):
        pass

    def connect(self):
        pass

    def getId(self):
        threads = []
        for verifier in Verifier.threads:
            threads.append(verifier.id)

        threads = sorted(threads)

        if len(threads) == 0:
            return 1

        elif len(threads) == 1:
            if threads[0] - 1 != 0:
                return 1
            else:
                return 2
        else:
            numGaps = False
            for i in range(len(threads) - 1):
                if threads[i + 1] - threads[i] == 1:
                    pass
                else:
                    numGaps = True
                    return threads[i] + 1

            if not numGaps:
                return threads[-1] + 1

    def doSomething(self, job, master):
        self.myJob = job
        self.active = True
        for account in self.myJob.accounts:
            master.writeToLog('Thread-' + str(self.id) + ': ' + account + '@' + self.myJob.host + str(self.myJob.id), 'OK')

        for account in self.myJob.custom:
            master.writeToLog('Thread-' + str(self.id) + ': ' + account + '@' + self.myJob.host , str(self.myJob.id), 'OK')

