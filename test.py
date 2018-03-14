import telnetlib
import time
import socket

def main():
    HOSTS = ['mx1.mac.gov.pl', 'smtp.mnisw.gov.pl', 'merkury04.mr.gov.pl', 'merkury04.mr.gov.pl', 'mail01.ron.mil.pl', 'znaczek.minrol.gov.pl', 'cdkadr.pl', 'kapuston.com']
    accounts = ['biuro', 'centrum', 'kadry', 'admin', 'dyrekcja', 'root']
    connected = False
    greeted = False
    mailFrom = False
    relayAllowed = True

    for host in HOSTS:
        try:
            connected = False
            greeted = False
            mailFrom = False
            replies = []
            stat = ''
            conn = telnetlib.Telnet(host, 25, timeout=10)
            if conn:
                connected = True
                time.sleep(2)
                #break

            if connected:

                reply = conn.read_until('\n')
                #print '0', reply
                if '554' in reply:
                    stat = 'delivery not allowed'
                    #mark as undetermined
                elif '450' in reply:
                    stat = 'no reverse'
                    #mark as udetermined
                elif '220' in reply:
                    conn.write('HELO hi'.encode('ascii') + b"\n")
                    reply = conn.read_until('\n')
                    if '250' in reply:
                        greeted = True
                        replies.append(reply)
                    else:
                        time.sleep(2)
                        conn.write('HELO hi'.encode('ascii') + b"\n")
                        reply = conn.read_until('\n')
                        if '250' in reply:
                            greeted = True
                    print '1', reply.rstrip()

                    if greeted:
                        for account in accounts:
                            print account
                            time.sleep(1)
                            if not mailFrom:
                                conn.write('MAIL from: me@my.com'.encode('ascii') + b"\n")
                                reply = conn.read_until('\n')
                                print reply
                                if '250' in reply:
                                    mailFrom = True
                                    #print '2', reply
                                    replies.append(reply)
                                elif '553' in reply:
                                    #can't get MailFrom, mark as undetermined
                                    break

                            if mailFrom:
                                conn.write('RCPT to: ' + account + '@cdkadr.pl'.encode('ascii') + b"\n")
                                reply = conn.read_until('\n')
                                print account, reply
                                if '250' in reply:
                                    #print '3',reply
                                    replies.append(account)
                                elif '554' in reply:
                                    stat = reply.rstrip()
                                    relayAllowed = False
                                    #set job as undetermined
                                    break
                                else:
                                    pass
                                    #print '4', reply

                        conn.write('QUIT'.encode('ascii') + b"\n")
                        print stat
                        print host, replies

            conn.close()
        except socket.timeout:
            print 'connection time-out. job outcome undetermind'
        except EOFError:
            print 'telnet connection was forcefully closed'



if __name__ == "__main__":
    main()