#  coding: utf-8 
import socketserver
import os
import re

# Copyright 2021 Abram Hindle, Eddie Antonio Santos, Steven Heung
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
# some of the code is Copyright © 2001-2021 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

DEBUG = True

## This assignment is heavily referenced from lab 2 regarding sending files
## Author: Zoe Rieli
## This assignment is also referenced from MDN Web Docs for HTTP Codes and their formats
## Author: Mozilla
## URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        if DEBUG:
            print ("\nGot a request of: %s\n" % self.data)
        
        httpHeaders = str(self.data).split("\\r\\n")
        requestData = httpHeaders[0].split()
        httpRequestCD = requestData[0][2:].strip()

        if DEBUG:
            print("\"" + httpRequestCD + "\"")

        #Handle request
        try:
            if (httpRequestCD == 'GET'):

                getFileLoc = requestData[1]
                print("Requested file location:", getFileLoc)
                self.__handle_get_request(getFileLoc)

            #Handle other request
            else:
                if DEBUG:
                    if httpRequestCD in ["POST", "PUT", "DELETE"]:
                        print("Unhandled request in POST/PUT/DELETE")
                    else:
                        print("Not Implemented:", httpRequestCD)
                self.request.sendall(bytes("HTTP/1.1 405 Method Not Allowed\r\n\r\n", "utf-8"))
        except Exception as e:
            #Something went wrong
            if DEBUG:
                print("Error:", str(e))
            self.request.sendall(bytes("HTTP/1.1 500 Internal Server Error\r\n\r\n", "utf-8"))
        finally:
            self.request.close()

    def __handle_get_request(self, location):
        """handle GET request"""
        baseWWWLocation = os.path.dirname(os.path.abspath(__file__)) + "/www"
        target = baseWWWLocation + str(location).strip()

        if DEBUG:
            print("Current target:", target)

        # check if target is a directory and properly enclosed with '/'. If so, show the index.html
        if os.path.isdir(target) and target[-1] == '/':
            file = target + "index.html"

            # check if the directory have an index.html
            if os.path.isfile(file):
                self.__read_and_send_file(file, contentType="text/html")
            else:
                if DEBUG:
                    print("Page do not have index.html")
                self.request.sendall(bytes("HTTP/1.1 404 Not Found\r\n", "utf-8"))

        # check if target is a valid file. If so, try to fetch the file
        elif self.__verify_file(target):
            file_type = target.split('/')[-1].split('.')[-1]
            if file_type == "css":
                self.__read_and_send_file(target, contentType="text/css")
            elif file_type == "html":
                self.__read_and_send_file(target, contentType="text/html")
            else:
                self.__read_and_send_file(target)

        # unable to find director or file
        else:
            # try to check if URL is improperly entered
            dirFix = target + '/'

            if DEBUG:
                print("Fixed DIR:", dirFix)

            if os.path.isdir(dirFix):
                # DIR can be fixed. Redirect.
                if DEBUG:
                    print("DIR exists after fixing")
                self.request.sendall(bytes("HTTP/1.1 301 Moved Permanently\r\n", "utf-8"))
                self.request.sendall(bytes("Location: http://{}:{}{}\r\n\r\n".format(HOST, PORT, str(location).strip()+ '/'), "utf-8"))
            else:
                # Send 404
                if DEBUG:
                    print("Unable to find page")
                self.request.sendall(bytes("HTTP/1.1 404 Not Found\r\n\r\n", "utf-8"))
    
    def __read_and_send_file(self, filePath, contentType=None):
        """Read html/css and send them to the request"""
        # get the current directory

        # send OK HTTP code and set content type
        self.request.sendall(bytes("HTTP/1.1 200 OK\r\n", "utf-8"))

        if contentType: #if content type is set, send the content type
            self.request.sendall(bytes("Content-Type: {0}\r\n\r\n".format(contentType.strip()), "utf-8"))
        else: # close the header
            self.request.sendall(bytes("\r\n", "utf-8"))
        
        # read bytes of the file
        with open(filePath, 'r') as file: 
            self.request.sendall(bytes(file.read(), "utf-8"))

    def __verify_file(self, target):
        """Verify if the file exists or if it is inside the www directory"""
        if os.path.isfile(target):
            baseWWWLocation = os.path.dirname(os.path.abspath(__file__)) + "/www"
            fileAbsPath = os.path.abspath(target) # find the absolute path of the file

            #using regex to check if the final directory starts with the base WWW location
            expression = "^" + baseWWWLocation + ".*"
            result = re.search(expression, fileAbsPath)
            if DEBUG:
                print("File Absolute Path:", fileAbsPath)
                print("Regex expression:", expression)
                print("Regex result:", result)
            
            if result:
                return True

        return False

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        exit()
