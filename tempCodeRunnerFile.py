    
      response = self.handle_request(data)      
      # return data to client
      connection.sendall(response) 
      connection.close()
      