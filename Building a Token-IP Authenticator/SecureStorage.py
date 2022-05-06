# COSC331 Lab 5
# Kyle Orcutt
# 300277486

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, time
from urllib import parse
import urllib.request

hostName = "localhost"
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    
    tokens = {}
    
    # Set the HTTP status code and response headers
    def set_headers(self, responseCode):
        self.send_response(responseCode)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Headers', "*")
        self.end_headers()
    
    def do_GET(self):
        if self.getPage() == '/':
            parameters = self.getParams()
            if parameters.get('token'):
                clientIP = self.client_address[0]
                fetchedIP = self.getToken(parameters.get('token'))
                if clientIP == fetchedIP:
                    self.set_headers(200)
                    self.wfile.write(bytes('My secret resource message', 'utf-8'))
                else:
                    self.set_headers(401)
                    self.wfile.write(bytes('Token does not match client.', 'utf-8'))
            else:
                self.set_headers(401)
                self.wfile.write(bytes('No token was provided.', 'utf-8'))
        else:
            self.set_headers(404)

    def getToken(self, token):
        # Fetches/caches a token for a set period of time, automatically re-fetches old tokens
        if token == 'logout':
            return None
        if token not in self.tokens.keys():
            try:
                fetchedIP = urllib.request.urlopen('http://127.0.0.1:8080/' + token).read()
                fetchedIP = fetchedIP.decode('utf-8')
                self.tokens[token] = [fetchedIP, time.time()]
            except:
                return None
            return fetchedIP
        else:
            tokenVals = self.tokens[token]
            if (time.time() - tokenVals[1]) < 300:
                del self.tokens[token]
                return self.getToken(token)
            else:
                return tokenVals[0]
            
    # Gets the query parameters of a request and returns them as a dictionary
    def getParams(self):
        output = {}
        queryList = parse.parse_qs(parse.urlsplit(self.path).query)
        for key in queryList:
            if len(queryList[key]) == 1:
                output[key] = queryList[key][0]
        return output
    
    # Returns a string containing the page (path) that the request was for
    def getPage(self):
        return parse.urlsplit(self.path).path

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started at 127.0.0.1:80")

    try:
        webServer.serve_forever()
    except:
        webServer.server_close()
        print("Server stopped.")
        sys.exit()

    webServer.server_close()
    print("Server stopped.")
    sys.exit()