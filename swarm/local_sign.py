import http.server
import threading
import json
from .exception import TransactionRejectedException
from urllib.parse import parse_qs, urlparse

DIRECTORY = "./swarm/local_sign_app/dist"

def getHandler(tx):
    class SigningHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args):
            self.tx = tx
            super().__init__(*args, directory=DIRECTORY)

        def do_GET(self) -> None:
            if self.path == '/' or self.path.startswith('/assets'):
                return super().do_GET()
            elif self.path.startswith('/params'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(tx).encode('UTF-8'))
                return
            
            elif self.path.startswith('/done'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{}')
                 
                query = parse_qs(urlparse(self.path).query)
                hash = query["txHash"][0]
                tx['return'] = hash
                
                print("Shutting down signing app.")
                threading.Thread(target=self.server.shutdown).start()

    return SigningHandler

async def local_sign(port, tx):
    with http.server.HTTPServer(("", port), getHandler(tx)) as httpd:
        print(f"Serving local signing app on http://localhost:{port}")
        httpd.serve_forever()

        if tx['return'] == 'rejected':
            raise TransactionRejectedException

        return tx['return']

