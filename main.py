import os
import socket
import mimetypes

# Class for logging connections
class Logger:
  file = None
  def __init__(self):
    
  def recordLog(self, data):
    pass

# Base for server
class TCPServer:
  def __init__(self, host = '127.0.0.1', port = 8888):
    self.host = host
    self.port = port
  
  def start(self):  
    # create socket obj
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind socket to address/port
    sock.bind((self.host, self.port))
    # listen for connections
    sock.listen(5)
    
    print("Socket is Listening on ", sock.getsockname())
    
    while True:
      # new connection
      connection, address = sock.accept()            
      print("Connection on ", address)
      # read data from client (first 104 bytes)
      data = connection.recv(1024)
      
      response = self.handle_request(data)      
      # return data to client
      connection.sendall(response)      
      connection.close()
      
  def handle_request(self, data):
    # handles incoming data and returns response
    return data
 
 
  
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

    # if check for requested page exists, else return 404 page
    if os.path.exists(filename):
      response_line = self.response_line(status_code=200)  
      
      # find file's MIME type, if nothing then 'text/html'
      content_type = mimetypes.guess_type(filename)[0] or 'text/html'      

      extra_headers = {'Content-Type': content_type}
      response_headers = self.response_headers(extra_headers)
      
      with open(filename, 'rb') as f:
        response_body = f.read()
        
    else:
      response_line = self.response_line(status_code=404)
      response_headers = self.response_headers()
      response_body = b"<h1>404 Not Found</h1>"      
    blank_line = b"\r\n"
    
    return b"".join([response_line, response_headers, blank_line, response_body])
    
  def handle_POST(self, request):
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
      

class HTTPRequest:
  def __init__(self, data):
    self.method = None
    self.uri = None
    self.http_version = "1.1"
    
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
  server.start()

      