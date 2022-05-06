# Kyle Orcutt

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64
from urllib import request, parse

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    
    # Set the HTTP status code and response headers
    def set_headers(self, responseCode):
        self.send_response(responseCode)
        self.send_header("Content-type", "text/html")
        self.send_header('Access-Control-Allow-Origin', "*")
        self.send_header('Access-Control-Allow-Headers', "*")
        self.end_headers()
    
        
    def do_POST(self):
        # TO-DO:
        # In this function, we need to do the following:
            
        # Catch user input from our HTML page
        requestData = self.getRequestData()
        
        # Generate a new RSA key for ourselves (we are using RSA Asymmetric Algorithm)
        myPrivateKey = rsa.generate_private_key(
            public_exponent = 65_537,
            key_size = 2_048,
            backend = default_backend()
            )
        
        # Get our public key from our private key object
        myPublicKey = myPrivateKey.public_key()
        
        # Generate a PEM formatted public key to share with the remote server
        myPEM = myPublicKey.public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
            )
        
        # Fetch the public key from the remote server, using the Public Key Reference
        publicKeyEndpoint = requestData.get('publickey')
        remotePEM = request.urlopen(publicKeyEndpoint).read()
        print(remotePEM)
        remotePublicKey = serialization.load_pem_public_key(remotePEM)
        
        # Use the remote public key to encrypt our message and encode it as a base64 string
        plaintext = requestData.get('plaintext')
        ciphertext = remotePublicKey.encrypt(bytes(plaintext, 'utf-8'), padding.PKCS1v15())
        print(ciphertext)
        ciphertext = base64.b64encode(ciphertext)
        print(ciphertext)
        
        # Send a request to the remote server with our encrypted message and our own PEM
        # We use the Encryption Endpoint URI as our target
        # We also have to decode our incoming response from base64
        encryptionEndpoint = requestData.get('endpoint')
        postParameters = parse.urlencode({'ciphertext' : ciphertext, 'publickey' : myPEM}).encode()
        encryptRequest = request.Request(encryptionEndpoint, data = postParameters)
        tokenResponse = request.urlopen(encryptRequest).read()
        tokenResponse = base64.b64decode(tokenResponse)
        
        # Now we need to decrypt the token we've received using our own private key
        decryptedToken = myPrivateKey.decrypt(tokenResponse, padding.PKCS1v15())
        decryptedToken = decryptedToken.decode('utf-8')
                
        # Create link URI pointing to our message stored on the remote server
        fetchURI = requestData.get('fetch');
        fetchURI += decryptedToken
        
        # Set headers and then return the link to the client
        self.set_headers(200)
        self.wfile.write(bytes('Your link: ' + fetchURI, 'utf-8'))

    def getRequestData(self):
        body = self.rfile.read(int(self.headers.get('Content-Length')))
        body = body.decode("utf-8")
        return dict(parse.parse_qsl(body))

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