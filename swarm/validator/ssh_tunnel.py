import subprocess
import time

class SSHTunnel:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def __enter__(self):
        self.tunnel = subprocess.Popen([
            'ssh',
            '-N',
            '-L',
            f'{self.port}:localhost:{self.port}',
            self.address
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(4) # HACK: wait for ssh tunnel to be ready!!

    def __exit__(self, exc_type, exc_value, traceback):
        self.tunnel.terminate()
        if exc_type is not None:
            print(exc_value, traceback)
            return False

