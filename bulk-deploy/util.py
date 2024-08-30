from web3 import Web3
import json

def int_to_address(i):
    hex_str = hex(i)[2:].zfill(40)
    addr = Web3.to_checksum_address('0x' + hex_str)
    return addr

def load_abi(path):
    with open(path, 'r') as f:
        abi = json.load(f)
        return abi
