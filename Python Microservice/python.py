# Kyle Orcutt

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:55:35 2020
@author: generic
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import time, sys, base64, json
from urllib import parse

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    history = []
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        # is home page?:
        if self.getPage() == '/':
            html = open("encryptionBase.html")
            htmlString = html.read()
            html.close()
            self.wfile.write(bytes(htmlString.replace("_PLACEHOLDER_", "You have not encrypted or decrypted anything yet"), "utf-8"))
        if self.getPage() == '/encrypt':
            params = self.getParams()
            encryptedText = self.encode(params['key'], params['plaintext'])
            self.history.append(encryptedText.decode("utf-8"))
            self.wfile.write(encryptedText)
        if self.getPage() == '/decrypt':
            params = self.getParams()
            decryptedText = self.decode(params['key'], params['ciphertext'])
            # dycrypt outputs a string so we need to convert to bytes
            self.wfile.write(bytes(decryptedText, "utf-8"))
        if self.getPage() == '/history':
            self.wfile.write(bytes(json.dumps(self.history), "utf-8"))
    
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
    
    def encode(self, key, plaintext):
        output = []
        for i in range(len(plaintext)):
            key_c = key[i % len(key)]
            enc_c = (ord(plaintext[i]) + ord(key_c)) % 256
            output.append(enc_c)
        return base64.urlsafe_b64encode(bytes(output))

    def decode(self, key, ciphertext):
        output = []
        ciphertext = base64.urlsafe_b64decode(ciphertext)
        for i in range(len(ciphertext)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ciphertext[i] - ord(key_c)) % 256)
            output.append(dec_c)
        return "".join(output)
            

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started at 127.0.0.1:8080")

    try:
        webServer.serve_forever()
    except:
        webServer.server_close()
        print("Server stopped.")
        sys.exit()

    webServer.server_close()
    print("Server stopped.")
    sys.exit()