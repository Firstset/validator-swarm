import subprocess
import time
import socket
from ..exception import SSHTunnelException

class SSHTunnel:
    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port

    def __enter__(self):
        ping = subprocess.Popen([
            'ssh', '-o', 'ConnectTimeout=2', self.address, 'exit'
            ])
        
        ping.wait()
        if ping.returncode != 0:
            raise SSHTunnelException(f'SSH address {self.address} is unreachable.')

        self.tunnel = subprocess.Popen([
            'ssh',
            '-N',
            '-L',
            f'{self.port}:localhost:{self.port}',
            self.address
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._wait_for_tunnel_ready(timeout=4) # seconds

    def __exit__(self, exc_type, exc_value, traceback):
        self.tunnel.terminate()
        if exc_type is not None:
            print(exc_value, traceback)
            return False
    
    def _wait_for_tunnel_ready(self, timeout: int) -> None:
        start_time = time.time()
        while True:
            try:
                with socket.create_connection(('localhost', self.port), timeout=1):
                    return  # Tunnel is ready
            except Exception as e :
                if time.time() - start_time > timeout:
                    raise SSHTunnelException(f'SSH tunnel to localhost:{self.port} not established within {timeout} seconds. {e}')
                time.sleep(0.5)  # Wait a bit before retrying
