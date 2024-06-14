import datetime
import os
import socket
import mimetypes
import atexit
from _thread import *
import threading


# Class for logging connections
class Logger:  
  def __init__(self):
    self.fileWrite = None
    self.fileRead = None
    self.fileName = "logs.txt"
    
  # make log entry
  def recordLog(self, *data):
    print(data)
    self.fileWrite = open(self.fileName, "a")        
    for log in data:
      entry = "%s at %s\n" % (log, datetime.datetime.now())
      self.fileWrite.write(entry)    
    self.fileWrite.close()
  
  # retrieve log records
  def getLogs(self):
    # records logs being retrieved
    log = "Logs retrieved from %s at %s\n" % ("user", datetime.datetime.now())
    open(self.fileName, "w").write(log)
    
    logs = open(self.fileName, "r").read()
    return logs
  

# Base for server
class TCPServer:
  def __init__(self, host = '127.0.0.1', port = 8888):
    self.host = host
    self.port = port
    self.logger = Logger()
    thread_lock = threading.Lock()
    
  def start(self):  
    # create socket obj
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind socket to address/port
    sock.bind((self.host, self.port))
    
    log = "\r\n---- Server started on %s:%s ----" % (self.host, self.port)
    self.logger.recordLog(log)
    
    # listen for connections
    sock.listen(5)
    
    print("Socket is Listening on ", sock.getsockname())
    
    while True:
      # new connection
      connection, address = sock.accept()   
      
      # Is now placed inside threadInstance()
      # gets ip of the requester
      # userIP = socket.gethostbyname(socket.gethostname())      
      # log = "Connection on {} from {}".format(address, userIP)
      # self.logger.recordLog(log)
      
      # initiate new thread instance
      # Note: adding param 'daemon' will cause all threads to terminate immediately if server is terminated
      newThread = threading.Thread(target=self.threadInstance, args=(connection, address,)) 
      newThread.start()
            
      # Is now placed inside threadInstance()
      # read data from client (first 1024 bytes)
      # data = connection.recv(1024)      
      # response = self.handle_request(data)      
      # # return data to client
      # connection.sendall(response) 
      # connection.close()
      
  def handle_request(self, data):
    # handles incoming data and returns response
    return data
  
  # Function for multi-threading
  def threadInstance(self, connection, address):
    # records request
    userIP = socket.gethostbyname(socket.gethostname())      
    log = "Connection on {} from {}".format(address, userIP)
    self.logger.recordLog(log)      
    
    # handles request
    data = connection.recv(1024)      
    response = self.handle_request(data)      
    
    # return data to client
    connection.sendall(response) 
    connection.close()
 
  
class HTTPServer(TCPServer):
  headers = {
    'Server': 'CrudeServer',
    'Content-Type': 'text/html',
  }
  
  status_codes = {
    200: 'OK',
    400: 'Bad Response',
    403: 'Forbidden',
    404: 'Not Found',
    500: "Internal Server Error",
    501: "Not Implemented",
  }
  
  # routes request to desired request method
  def handle_request(self, data):
    request = HTTPRequest(data)
    
    try:
      # get request method and call appropriate handler
      handler = getattr(self, 'handle_%s' % request.method)
    except:
      handler = self.HTTP_501_handler
      
    response = handler(request)    
    return response
  
  # handles unhandled requests
  def HTTP_501_handler(self, request):
    response_line = self.response_line(status_code=501)
    response_headers = self.response_headers()
    blank_line = b"\r\n"
    response_body = b"<h1>501 Not Implemented</h1>"
    return b"".join([response_line, response_headers, blank_line, response_body])
    
  
  def handle_GET(self, request):
    filename = request.uri.strip('/') # removes slash from request URI
    status=0
    response_headers=""
    # if check for requested page exists, else return 404 page
    if os.path.exists(filename):
      status=200
      response_line = self.response_line(status_code=200)  
      
      # find file's MIME type, if nothing then 'text/html'
      content_type = mimetypes.guess_type(filename)[0] or 'text/html'      

      extra_headers = {'Content-Type': content_type}
      response_headers = self.response_headers(extra_headers)
      
      with open(filename, 'rb') as f:
        response_body = f.read()
        
    else:
      status=404
      response_line = self.response_line(status_code=404)
      response_headers = self.response_headers()
      response_body = b"<h1>404 Not Found</h1>"      
    blank_line = b"\r\n"    

    if not filename: filename="/"
      
    log = "{} for {} {}".format(status, request.method, filename)
    self.logger.recordLog(log)
    
    return b"".join([response_line, response_headers, blank_line, response_body])
    
  def handle_POST(self, request):
    print("Attempted post")
    pass
  
  def handle_DELETE(self, request):
    pass
  
  
  def response_line(self, status_code):
    reason = self.status_codes[status_code]
    line = "HTTP/1.1 %s %s\r\n" % (status_code, reason)
    
    return line.encode() # converts str to bytes
  
  
  def response_headers(self, extra_headers=None):
    """ 'extra_headers' can be a dict for sending extra headers for current response """
    headers_copy = self.headers.copy()
    
    if extra_headers:
      headers_copy.update(extra_headers)
      
    headers = ""
    
    for h in headers_copy:
      headers += "%s: %s\r\n" % (h, headers_copy[h])
      
    return headers.encode() # encodes str to bytes
  
  # records server close
  def handle_EXIT(self):
    log = "<<< Closing server >>> " 
    self.logger.recordLog(log)


class HTTPRequest:
  def __init__(self, data):
    self.method = None
    self.uri = None
    self.http_version = "1.1"
    # self.ip = 
    
    self.parse(data)
    
  def parse(self, data):
    lines = data.split(b"\r\n")
    request_line = lines[0]
    words = request_line.split(b" ")
    self.method = words[0].decode()
    
    if len(words) > 1:
      # some browsers dont send uri for homepage
      self.uri = words[1].decode()
      
    if len(words) > 2:
      self.http_version = words[2]

  
if __name__ == '__main__':
  server = HTTPServer()
  try:
    server.start()
    atexit.register(server.handle_EXIT)
  except Exception as e:
    server.handle_EXIT()
  finally:
    server.handle_EXIT()
  
# multi-threading for multiple clients

      