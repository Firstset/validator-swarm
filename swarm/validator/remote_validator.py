import json
import requests
from .validator import Validator, SSHTunnel

class RemoteValidator(Validator):
    
    def __init__(self, config):
        self.ssh_address = config['validator_api']['ssh_address']
        self.keymanager_port = config['validator_api']['port']
        self.auth_token = config['validator_api']['auth_token']
        
        self.remote_signer_ssh_address = config['remote_signer']['ssh_address']
        self.remote_signer_port = config['remote_signer']['port']
        self.remote_signer_auth_token = config['remote_signer']['auth_token']
        
        self.remote_signer_url = config['remote_signer']['url']
        
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'ContentType': 'application/json'
        }

    def load_keys(self, keystores, passwd):
        # if loading keys to remote signer fails, exception is thrown
        # and is caught by main
        self.load_keys_to_remote_signer(keystores, passwd) 
        self.load_remote_keys_to_validator_client(keystores)

    def remove_keys(self, keystores):
        self.remove_keys_from_remote_signer(keystores)
        self.remove_remote_keys_from_validator_client(keystores)

    def load_keys_to_remote_signer(self, keystores, passwd):
        passwords = [passwd] * len(keystores)
        data = {
            'keystores': [json.dumps(x) for x in keystores],
            'passwords': passwords
        }
        remote_signer_endpoint = f'http://localhost:{self.remote_signer_port}/eth/v1/keystores'

        # load validators into lighthouse
        headers = {
            'Authorization': f'Bearer {self.remote_signer_auth_token}',
            'ContentType': 'application/json'
        }
        with SSHTunnel(self.remote_signer_ssh_address, self.remote_signer_port):
            # check if the keys are deployed
            response = requests.get(url=remote_signer_endpoint, headers=headers)
            response_json = response.json()
            
            added_keylist = [k['validating_pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]
            
            if any([x in added_keylist for x in new_keylist]):
                raise Exception('The submitted keys are already loaded into the remote signer.')

            response = requests.post(url=remote_signer_endpoint, headers=headers, json=data)
            if response.status_code != 200:
                raise Exception(f'Submission of keys to remote signer unsuccessful. Status code: {response.status_code}')
            print(response.json(), flush=True) 
        
        if response.status_code == 200:
            print('Loaded keystores into remote signer successfuly')
    
    def load_remote_keys_to_validator_client(self, keystores):
        validator_endpoint = f'http://localhost:{self.keymanager_port}/eth/v1/remotekeys'
        validator_data = {
                'remote_keys': []
        }
        
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'ContentType': 'application/json'
        }

        for k in keystores:
            d = {'pubkey': f'0x{k["pubkey"]}', 'url': self.remote_signer_url}
            validator_data['remote_keys'].append(d)

        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=validator_endpoint, headers=headers)
            response_json = response.json()
            
            added_keylist = [k['pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]
            
            if any([x in added_keylist for x in new_keylist]):
                raise Exception('The submitted keys are already loaded into the validator client.')

            response = requests.post(url=validator_endpoint, headers=headers, json=validator_data)
            if response.status_code != 200:
                raise Exception(f'Submission of keys to validator client unsuccessful. Status code: {response.status_code}')

    def remove_keys_from_remote_signer(self, keystores):
        
        pubkeys = [f'0x{x["pubkey"]}' for x in keystores]
        data = {
            'pubkeys': pubkeys
        }

        # load validators into lighthouse
        url = f'http://localhost:{self.remote_signer_port}/eth/v1/keystores'
        headers = {
            'Authorization': f'Bearer {self.remote_signer_auth_token}',
            'ContentType': 'application/json'
        }
        with SSHTunnel(self.remote_signer_ssh_address, self.remote_signer_port):
            response = requests.delete(url=url, headers=headers, json=data)
            print(response.json(), flush=True) 
        if response.status_code != 200:
            raise Exception(f'while deleting keystores from remote signer: {response.status_code}')

        print('Deleted keystores from remote signer successfuly')

    def remove_remote_keys_from_validator_client(self, keystores):
        
        validator_endpoint = f'http://localhost:{self.keymanager_port}/eth/v1/remotekeys'
        validator_data = {
                'pubkeys': []
        }
        
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'ContentType': 'application/json'
        }

        validator_data['pubkeys'] = [f'0x{k["pubkey"]}' for k in keystores] 

        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.delete(url=validator_endpoint, headers=headers)
            print(response.json(), flush=True)
            
            if response.status_code != 200:
                raise Exception(f'while deleting remote keys from validator client. Status code: {response.status_code}')
