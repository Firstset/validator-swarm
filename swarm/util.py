from swarm.exception import ConfigException
from web3 import Web3
import json
import os
from urllib.parse import urlparse

def int_to_address(i: int) -> str:
    hex_str = hex(i)[2:].zfill(40)
    addr = Web3.to_checksum_address('0x' + hex_str)
    return addr

def load_json_file(path: str) -> dict:
    with open(path, 'r') as f:
        data = json.load(f)
        return data

def is_well_formed_url(url: str, protocol: str) -> bool:
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme == protocol and parsed_url.hostname and parsed_url.port:
            return True
        return False

    except ValueError:
        return False

def is_file_executable(filepath: str) -> bool:
    if os.path.isfile(filepath):
        if os.access(filepath, os.X_OK):
            return True
    return False

def load_chain_addresses(config: dict) -> dict:
    """
    Load chain-specific addresses from JSON file and inject them into config.
    Returns the modified config dict.
    """
    chain = config['chain'].lower()
    addresses_file = os.path.join(os.getcwd(), 'addresses', f'{chain}.json')
    try:
        addresses = load_json_file(addresses_file)
    except Exception as e:
        raise ConfigException(f'Failed to load addresses for chain {chain}: {e}')

    # Inject addresses into config
    if 'contracts' not in config['csm']:
        config['csm']['contracts'] = {}
        
    config['csm']['contracts'].update({
        'module_address': addresses['csm']['module_address'],
        'accounting_address': addresses['csm']['accounting_address'],
        'VEBO_address': addresses['csm']['VEBO_address']
    })
    
    # Add withdrawal address
    config['deposit']['withdrawal_address'] = addresses['withdrawal_address']

    # Add relay allowlist address
    config['relay_allowlist_address'] = addresses['relay_allowlist_address']

    # Add fee recipient
    config['fee_recipient'] = addresses['fee_recipient']

    return config
