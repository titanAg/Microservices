# Kyle Orcutt

# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 12:52:31 2020

@author: generic
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 01:03:56 2020

@author: KoBoLd
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import time, json
from urllib import parse
from json import JSONDecodeError

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    
    myDict = {}
    
    # You can pass an integer statusCode (i.e. 200, 404, etc) to this function to return a specific HTTP status
    def set_headers(self, statusCode):
        self.send_response(statusCode)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Headers', "*")
        self.send_header('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, PATCH, OPTIONS")
        self.end_headers()
    
    def do_GET(self):
        print("GET REQUEST")
        if self.getURI() in self.myDict.keys():
            parameters = self.getParams()
            if parameters.get('key'):
                jsonObject = json.loads(self.myDict[self.getURI()])
                value = jsonObject.get(parameters.get('key'))
                if value:
                    self.set_headers(200)
                    self.wfile.write(bytes(json.dumps(value), "utf-8"))
                else:
                    self.set_headers(404)
            else:
                self.set_headers(200)
                self.wfile.write(bytes(self.myDict[self.getURI()], "utf-8"))
        else:
            self.set_headers(404)
        
    def do_POST(self):
        print("POST REQUEST")
        if self.getURI() not in self.myDict.keys():
            try:
                # json.loads -> deserialization
                newObject = json.loads(str(self.getBody().decode("utf-8")))
                if isinstance(newObject, dict):
                    # json.dumps -> serialization
                    self.myDict[self.getURI()] = json.dumps(newObject)
                    self.set_headers(201)
                else:
                    self.set_headers(400)
            except JSONDecodeError:
                self.set_headers(400)
        else:
            self.set_headers(409)
        
    def do_PUT(self):
        print("PUT REQUEST")
        if self.getURI() in self.myDict.keys():
            try:
                # json.loads -> deserialization
                newObject = json.loads(str(self.getBody().decode("utf-8")))
                if isinstance(newObject, dict):
                    # json.dumps -> serialization
                    self.myDict[self.getURI()] = json.dumps(newObject)
                    self.set_headers(200)
                else:
                    self.set_headers(400)
            except JSONDecodeError:
                self.set_headers(400)
        else:
            self.set_headers(404)
        
    def do_DELETE(self):
        print("DELETE REQUEST")
        if self.getURI() in self.myDict.keys():
            self.set_headers(200)
            self.myDict.pop(self.getURI(), None)
        else:
            self.set_headers(404)
        
    def do_PATCH(self):
        print("PATCH REQUEST")
        if self.getURI() in self.myDict.keys():
            oldData = json.loads(self.myDict[self.getURI()])
            try:
                # json.loads -> deserialization
                newData = json.loads(str(self.getBody().decode("utf-8")))
                if isinstance(newData, dict):
                    for key in newData.keys():
                        oldData[key] = newData[key]
                    self.myDict[self.getURI()] = json.dumps(oldData)
                    self.set_headers(200)
                else:
                    self.set_headers(400)
            except JSONDecodeError:
                self.set_headers(400)                
        else:
            self.set_headers(404)
        
    # This is necessary, as OPTIONS is used to check if the service supports HTTP 1.1 verbs (PUT, PATCH, DELETE)    
    def do_OPTIONS(self):
        self.set_headers(200)
        
    # This function retrieves the current URI that has been requested by the client   
    def getURI(self):
        return parse.urlsplit(self.path).path
    
    # This function gets any query string parameters that were part of the request
    def getParams(self):
        output = {}
        queryList = parse.parse_qs(parse.urlsplit(self.path).query)
        for key in queryList:
            if len(queryList[key]) == 1:
                output[key] = queryList[key][0]
        return output
    
    # This function retrieves the request body data
    def getBody(self):
        return self.rfile.read(int(self.headers.get('Content-Length')))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    webServer.serve_forever()