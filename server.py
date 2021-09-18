#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        httpHeaders = str(self.data).split("\\r\\n")
        requestData = httpHeaders[0].split()
        httpRequestCD = requestData[0][2:].strip()
        print("\"" + httpRequestCD + "\"")

        #Handle get request
        if (httpRequestCD == 'GET'):

            getFileLoc = requestData[1]
            print("Requested file location:", getFileLoc)
            self.send_request_file(getFileLoc)
        #Handle other request
        else:
            if httpRequestCD in ["POST", "PUT", "DELETE"]:
                print("Unhandled request in POST/PUT/DELETE")
            else:
                print("Not Implemented")

            self.request.sendall(bytes("HTTP/1.1 405 Method Not Allowed\n", "utf-8"))

        self.request.close()

    def send_request_file(self, location):
        location = str(location).strip()
        currentFileLocation = os.path.dirname(os.path.abspath(__file__))
        if location == "/":
            # send OK HTTP code and set content type
            self.request.send(bytes("HTTP/1.1 200 OK\n", "utf-8"))
            self.request.send(bytes("Content-Type: text/html\n\n", "utf-8"))

            with open(currentFileLocation + "/www/index.html", 'rb') as indexFile: # read bytes of the index file
                self.request.sendfile(indexFile)
        
            


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(e.args)
        exit(1)
