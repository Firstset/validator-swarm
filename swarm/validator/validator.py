import json
from typing import List
from eth_typing import Address
import requests

from swarm.exception import ValidatorDeleteException, ValidatorLoadException, ValidatorReadException
from .ssh_tunnel import SSHTunnel

class Validator():
    
    def __init__(self, config: dict) -> None:
        self.ssh_address = config['validator_api']['ssh_address']
        self.keymanager_port = config['validator_api']['port']

        self.headers = {
            'Authorization': f'Bearer {config["validator_api"]["auth_token"]}',
            'ContentType': 'application/json'
        }

    def load_keys(self, keystores: List[dict], passwd: str) -> None:
        # get keys
        passwords = [passwd] * len(keystores)
        data = {
            'keystores': [json.dumps(x) for x in keystores],
            'passwords': passwords
        }
        url = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'

        # load validators into lighthouse
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            
            added_keylist = [k['validating_pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]
            
            if any([x in added_keylist for x in new_keylist]):
                raise ValidatorLoadException('The submitted keys are already loaded into the validator.')

            response = requests.post(url=url, headers=self.headers, json=data)
            if response.status_code != 200:
                raise ValidatorLoadException(f'Submission of keys to validator client unsuccessful. Status code: {response.status_code}')
            if any(f['status'] != 'imported' for f in response.json()['data']):
                raise ValidatorLoadException(f'One or more keys were not loaded into the validator client.')
            print(response.json(), flush=True) 
        
        if response.status_code == 200:
            print('Loaded keystores into validator successfuly')
        
    def load_remote_keys(self, keystores: List[dict], remote_signer_url: str) -> None:
        validator_remotekeys_endpoint = f'http://localhost:{self.keymanager_port}/eth/v1/remotekeys'
        validator_keystores_endpoint = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'
        validator_data = {
            'remote_keys': []
        }
        
        for k in keystores:
            d = {'pubkey': f'0x{k["pubkey"]}', 'url': remote_signer_url}
            validator_data['remote_keys'].append(d)

        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=validator_keystores_endpoint, headers=self.headers)
            response_json = response.json()
            
            added_keylist = [k['validating_pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]

            if any([x in added_keylist for x in new_keylist]):
                raise ValidatorLoadException('The submitted keys are already loaded into the validator client.')

            response = requests.post(url=validator_remotekeys_endpoint, headers=self.headers, json=validator_data)
            print(response.json(), flush=True) 
            if response.status_code != 200:
                raise ValidatorLoadException(f'Submission of keys to validator client unsuccessful. Status code: {response.status_code}')
            if any(f['status'] != 'imported' for f in response.json()['data']):
                raise ValidatorLoadException(f'One or more keys were not loaded into the validator client.')
            print("Loaded remote keys into validator successfuly")

    def remove_keys(self, pubkeys: List[Address]) -> None:
        data = {
            'pubkeys': pubkeys
        }

        # load validators into lighthouse
        url = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            response = requests.delete(url=url, headers=self.headers, json=data)
            print(response.json(), flush=True) 
        if response.status_code != 200:
            raise ValidatorDeleteException(f'while deleting keystores from validator: {response.status_code}')

        print('Deleted keystores from validator successfuly')

    def remove_remote_keys(self, pubkeys: List[Address]) -> None:
        
        data = {
            'pubkeys': pubkeys
        }

        # load validators into lighthouse
        url = f'http://localhost:{self.keymanager_port}/eth/v1/remotekeys'
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            response = requests.delete(url=url, headers=self.headers, json=data)
            print(response.json(), flush=True) 
        if response.status_code != 200:
            raise ValidatorDeleteException(f'while deleting remote keys from validator: {response.status_code}')

        print('Deleted remote keys from validator successfuly')

    def get_loaded_keys(self) -> List[Address]:
        print('Fetching all keys registered in validator...')
        # get keys
        url = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'

        # load validators into lighthouse
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            
            if response.status_code != 200:
                raise ValidatorReadException(f'error reading keys loaded in validator client')
        
        added_keys = [k["validating_pubkey"] for k in response_json['data']]
        return added_keys
    
    def get_remote_keys(self) -> List[Address]:
        # get keys
        url = f'http://localhost:{self.keymanager_port}/eth/v1/remotekeys'

        # load validators into lighthouse
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            
            if response.status_code != 200:
                raise ValidatorReadException(f'error reading remote keys loaded in validator client')
        
        added_keys = [k["pubkey"] for k in response_json['data']]
        return added_keys
