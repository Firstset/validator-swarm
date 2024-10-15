from web3 import Web3
import json
import os
from urllib.parse import urlparse

def int_to_address(i):
    hex_str = hex(i)[2:].zfill(40)
    addr = Web3.to_checksum_address('0x' + hex_str)
    return addr

def load_abi(path):
    with open(path, 'r') as f:
        abi = json.load(f)
        return abi

def is_well_formed_url(url, protocol):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme == protocol and parsed_url.hostname and parsed_url.port:
            return True
        return False

    except ValueError:
        return False

def is_file_executable(filepath):
    if os.path.isfile(filepath):
        if os.access(filepath, os.X_OK):
            return True
    return False
