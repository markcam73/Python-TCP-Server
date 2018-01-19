#TCPServer.py
from socket import socket, SOCK_STREAM, AF_INET
import os
from time import time
from datetime import datetime

def getLastMod(filename):
  last_modified_date = datetime.fromtimestamp(os.path.getmtime(filename))
  http_format = time.strftime('%a, %d %b %Y %H:%M:%S GMT', last_modified_date)
  return http_format

def getIfModSince(message):
  header_index = message.find("If-Modified-Since: ")
  if header_index > 0:
    request_date = message[header_index + 19:Header_index + 48]
    date = time.strptime(request_date, '%a, %d %b %Y %H:%M:%S GMT')
    return date
  return 0

def getHeaders(message):
  fields = message.split("\r\n")
  fields = fields[1:]
  output = {}
  for field in fields:
    key,colon,value = field.partition(':')
    output[key] = value
  return output

def getLanguageRequests(headers):
  lang_req = ""
  lang_map = {}
  for key in headers:
    if key == "Accept-Language":
        lang_req = headers[key][1:]
  print lang_req
  requests = lang_req.split(",")
  for req in requests:
    key,semicolon,value = req.partition(';')
    lang_map[key] = value
  for key in lang_map:
    print key, '+' ,lang_map[key]
  return lang_map

def searchLanguage(lang_req, filename):
  for key in lang_req:
    for file in os.listdir('.'):
      if file.endswith(key):
        filename = file
        print filename
        return


#Create a TCP socket
#Notice the use of SOCK_STREAM for TCP packets
serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort=12333
# Assign IP address and port number to socket
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print "Interrupt with CTRL-C"
while True:
        try:
                connectionSocket, addr = serverSocket.accept()
                print "Connection from %s port %s" % addr
                # Receive the client packet
                message = connectionSocket.recv(4096)
                print message,'::',message.split()[0],':',message.split()[1]
                filename = message.split()[1].partition("/")[2]
                print filename
                headers = getHeaders(message)
                for key in headers:
                        print key
                lang_req = getLanguageRequests(headers)
                try:
                        searchLanguage(lang_req, filename)
                        f = open(filename, 'r')
                        outputdata = f.read()
                        print outputdata
                        request_time = getIfModSince(message)
                        if request_time > 0:
                          file_time = getLastMod(filename)
                          if file_time < request_time:
                            print 'File up to date'
                            connectionSocket.send('HTTP/1.1 304 Not Modified\r\n')
                            connectionSocket.send('Content-Type: text/plain\r\n')
                            connectionSocket.send('Last-Modified: '+ file_time +'\r\n\r\n')
                            connectionSocket.close
                            break
                        connectionSocket.send('HTTP/1.1 200 OK\r\n')
                        connectionSocket.send('Content-Type: text/html\r\n\r\n')
                        connectionSocket.send(outputdata)
                        connectionSocket.close()
                        f.close()
                except IOError:
                        print 'File not found'
                        f = open('notfound.html')
                        connectionSocket.send('HTTP/1.1 404 Not Found\r\n')
                        connectionSocket.send('Content-Type: text/html\r\n\r\n')
                        connectionSocket.send(f.read())
                        connectionSocket.close()
                        f.close()
        except KeyboardInterrupt:
                print "\nInterrupted by CTRL-C"
                break
serverSocket.close()
