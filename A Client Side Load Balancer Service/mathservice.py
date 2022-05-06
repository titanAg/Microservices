# Kyle Orcutt

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from urllib import parse

hostName = "localhost"
serverPort = 8080
ports = ["8080","8081","8082"]

class MyServer(BaseHTTPRequestHandler):    
        
    def do_GET(self):
        # Here, we'll fetch a 'number' parameter from the incoming GET request
        # We'll print the incoming request number to the console
        # Then, we'll perform an iterative calculation on it - summing all values less than or equal to the input
        # We'll then return the number
        data = self.getParams()
        print("Got request for " + data['number'])
        output = 0
        for x in range(int(data['number']) + 1):
            output += x
        self.set_headers(200)
        self.wfile.write(bytes("<h1>Triangular Number: " + str(output),"utf-8"))
        
    # Gets the query parameters of a request and returns them as a dictionary
    def getParams(self):
        output = {}
        queryList = parse.parse_qs(parse.urlsplit(self.path).query)
        for key in queryList:
            if len(queryList[key]) == 1:
                output[key] = queryList[key][0]
        return output
    
    # Set the HTTP status code and response headers
    def set_headers(self, responseCode):
        self.send_response(responseCode)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Headers', "*")
        self.end_headers()

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except:
        webServer.server_close()
        print("Server stopped.")
        sys.exit()
    webServer.server_close()
    print("Server stopped.")
    sys.exit()