import os

host = 'umig.miastko.pl'

server = os.popen('nslookup -q=mx ' + host).readlines()
print server
server = [x.rstrip() for x in server if 'exchanger' in x]

mx_list = []

for i in server:
    line = i.split(',')
    mx_list.append((line[0].split('=')[-1].strip(), line[1].split('=')[-1].strip()))

print sorted(mx_list)

