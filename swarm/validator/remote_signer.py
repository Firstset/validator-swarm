import json
import requests

from swarm.exception import ValidatorDeleteException, ValidatorLoadException, RemoteSignerURLException, ValidatorReadException
from .validator import SSHTunnel
from ..util import is_well_formed_url

class RemoteSigner():
    
    def __init__(self, config):
        
        self.remote_signer_ssh_address = config['remote_signer']['ssh_address']
        self.remote_signer_port = config['remote_signer']['port']
        
        self.remote_signer_url = config['remote_signer']['url']
        if not is_well_formed_url(f'{self.remote_signer_url}', 'http'):
            raise RemoteSignerURLException('Remote signer URL is not well formed. check config file.')

        self.headers = {
            'ContentType': 'application/json'
        }


    def load_keys(self, keystores, passwd):
        passwords = [passwd] * len(keystores)
        data = {
            'keystores': [json.dumps(x) for x in keystores],
            'passwords': passwords
        }
        remote_signer_endpoint = f'http://localhost:{self.remote_signer_port}/eth/v1/keystores'

        # load validators into lighthouse
        with SSHTunnel(self.remote_signer_ssh_address, self.remote_signer_port):
            # check if the keys are deployed
            response = requests.get(url=remote_signer_endpoint, headers=self.headers)
            response_json = response.json()
            
            added_keylist = [k['validating_pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]
            
            if any([x in added_keylist for x in new_keylist]):
                raise ValidatorLoadException('The submitted keys are already loaded into the remote signer.')

            response = requests.post(url=remote_signer_endpoint, headers=self.headers, json=data)
            if response.status_code != 200:
                raise ValidatorLoadException(f'Submission of keys to remote signer unsuccessful. Status code: {response.status_code}')
            print(response.json(), flush=True) 
        
        if response.status_code == 200:
            print('Loaded keystores into remote signer successfuly')
    

    def remove_keys(self, pubkeys):
        
        data = {
            'pubkeys': pubkeys
        }

        # load validators into lighthouse
        url = f'http://localhost:{self.remote_signer_port}/eth/v1/keystores'
        with SSHTunnel(self.remote_signer_ssh_address, self.remote_signer_port):
            response = requests.delete(url=url, headers=self.headers, json=data)
            print(response.json(), flush=True) 
        if response.status_code != 200:
            raise ValidatorDeleteException(f'while deleting keystores from remote signer: {response.status_code}')

        print('Deleted keystores from remote signer successfuly')


    def get_loaded_keys(self):
        print('Fetching all keys registered in remote signer...')
        # get keys
        url = f'http://localhost:{self.remote_signer_port}/eth/v1/keystores'

        with SSHTunnel(self.remote_signer_ssh_address, self.remote_signer_port):
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            
            if response.status_code != 200:
                raise ValidatorReadException(f'error reading keys loaded in remote signer')
        
        added_keys = [k["validating_pubkey"] for k in response_json['data']]
        return added_keys
        


