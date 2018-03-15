import threading
import time
import os
from job import *
import telnetlib
import socket

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
                        if not job.mx:
                            self.master.verifierLog.append(('TH-' + str(self.id) + ': Looking up MX records for ' + job.host, 'NA'))
                            lookup = os.popen('nslookup -q=mx ' + job.host).readlines()

                            lookup = [x.rstrip() for x in lookup if 'exchanger' in x]

                            for i in lookup:
                                line = i.split(',')
                                job.mx.append((line[0].split('=')[-1].strip(), line[1].split('=')[-1].strip()))

                            self.master.lock.release()

                        else:
                            self.master.lock.release()

                        if job.mx:
                            self.master.verifierLog.append(('TH-' + str(self.id) + ': Found ' + str(len(job.mx)) + ' MX record(s) for host ' + job.host, 'OK'))
                            for pri, mxServer in job.mx:
                                try:
                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': Trying to establish connection with ' + mxServer, 'NA'))
                                    conn = telnetlib.Telnet(mxServer, 25, timeout=10)
                                    if conn:
                                        self.master.verifierLog.append(('TH-' + str(self.id) + ': Successfuly opened connection to ' + mxServer, 'OK'))
                                        job.connected = True
                                        job.mxServer = mxServer
                                        time.sleep(2)
                                        break

                                except socket.timeout:
                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': Connection time-out for ' + job.mxServer, 'OK'))
                                    print 'connection time-out. job outcome undetermind'

                                except EOFError:
                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': Telnet connection for ' + job.mxServer + ' was forcefully closed', 'OK'))
                                    print 'telnet connection was forcefully closed'

                            if job.connected:
                                reply = conn.read_until('\n')
                                print '0', reply.rstrip()
                                if '554' in reply:
                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + job.mxServer + ' doesn\'t allow communication via Telnet protocol, assuming all main emails valid for ' + job.host, 'FAIL'))
                                    job.status = 'UND'
                                elif '450' in reply:
                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + job.mxServer + ' couldn\'t find reverse hostname for your IP, assuming all main emails valid for ' + job.host, 'FAIL'))
                                    job.status = 'UND'
                                elif '220' in reply:
                                    conn.write('HELO hi'.encode('ascii') + b"\n")
                                    reply = conn.read_until('\n')
                                    if '250' in reply:
                                        self.master.verifierLog.append(('TH-' + str(self.id) + ': Managed successful handshake with ' + job.mxServer, 'OK'))
                                        job.greeted = True
                                    else:
                                        time.sleep(2)
                                        conn.write('HELO hi'.encode('ascii') + b"\n")
                                        reply = conn.read_until('\n')
                                        if '250' in reply:
                                            self.master.verifierLog.append(('TH-' + str(self.id) + ': Managed successful handshake with ' + job.mxServer, 'OK'))
                                            job.greeted = True

                                    print '1', reply.rstrip()

                                    if job.greeted:
                                        for (id, (account, type, result)) in enumerate(job.accounts):
                                            time.sleep(1)
                                            if not job.mailFrom:
                                                conn.write('MAIL from: me@my.com'.encode('ascii') + b"\n")
                                                reply = conn.read_until('\n')
                                                print '2', reply.rstrip()
                                                if '250' in reply:
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': Server ' + job.mxServer + ' accepted "MAIL from" command', 'OK'))
                                                    job.mailFrom = True
                                                elif '553' in reply:
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + job.mxServer + ' rejected "MAIL from" command, assuming all main emails valid for ' + job.host, 'FAIL'))
                                                    job.status = 'UND'
                                                    break

                                            if job.mailFrom and job.relayAllowed:
                                                conn.write('RCPT to: ' + (account + '@' + job.host).encode('ascii') + b"\n")
                                                reply = conn.read_until('\n')
                                                print '3', reply.rstrip()
                                                if '250' in reply:
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + account + '@' + job.host + ' successfully verified as existing on host domain', 'IN'))
                                                    Verifier.verified += 1
                                                    job.accounts[id][-1] = True
                                                    print job.accounts[id]
                                                    if type == 'main':
                                                        Job.jobsResultsMain.append(account + '@' + job.host)
                                                    else:
                                                        Job.jobsResultsCustom.append(account + '@' + job.host)
                                                    job.replies.append(account)
                                                    job.serverResponsive = True
                                                elif '550' in reply:
                                                    Verifier.verified += 1
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + account + '@' + job.host + ' doesn\'t exist on host domain', 'FAIL'))
                                                    job.accounts[id][-1] = False
                                                    if type == 'main':
                                                        Job.jobsResultsMainFailed.append(account + '@' + job.host)
                                                    else:
                                                        Job.jobsResultsCustomFailed.append(account + '@' + job.host)
                                                    job.serverResponsive = True
                                                elif '554' in reply:
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + job.mxServer + ' declined relying, assuming all main emails valid for ' + job.host, 'FAIL'))
                                                    job.status = 'UND'
                                                    job.relayAllowed = False
                                                    break
                                                elif '450' in reply:
                                                    self.master.verifierLog.append(('TH-' + str(self.id) + ': ' + job.mxServer + ' host could not find your reverse hostname, assuming all main emails valid for ' + job.host, 'FAIL'))
                                                    job.status = 'UND'
                                                    break
                                                else:
                                                    pass

                                        conn.write('QUIT'.encode('ascii') + b"\n")
                                        job.status = 'DONE'
                                        print job.host, job.replies

                                    else:
                                        job.greeted = False
                                        self.master.verifierLog.append(('TH-' + str(self.id) + ': Failed to handshake with the server, assuming all main emails valid for ' + job.host, 'FAIL'))
                                        job.status = 'UND'
                                    conn.close()

                            else:
                                self.master.verifierLog.append(('TH-' + str(self.id) + ': Failed to establish connection with any of the MX servers for ' + job.host + ' assuming all main emails valid', 'FAIL'))
                                job.status = 'UND'

                        else:
                            self.master.verifierLog.append(('TH-' + str(self.id) + ': No MX records for ' + job.host + " found or host doesn't exist. Dropping all e-mails from queue.", 'FAIL'))
                            job.status = 'DEAD'

                        if job.status == 'DEAD':
                            print 'no jobs saved'
                        elif job.status == 'UND':
                            for account, type, result in job.accounts:
                                if type == 'MAIN' and result != False:
                                    Job.jobsResultsMain.append(account + '@' + job.host)

                    else:
                        self.master.lock.release()
                        self.active = False
                        print Job.jobsResultsMain
                        print Job.jobsResultsMainFailed
                        print Job.jobsResultsCustom
                        print Job.jobsResultsCustomFailed
                else:
                    self.active = False
