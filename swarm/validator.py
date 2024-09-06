import json
import subprocess
import time
import requests

class SSHTunnel:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def __enter__(self):
        print("Opening ssh tunnel...")
        self.tunnel = subprocess.Popen([
            'ssh',
            '-N',
            '-L',
            f'{self.port}:localhost:{self.port}',
            self.address
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(4) # HACK: wait for ssh tunnel to be ready!!
        print("ssh tunnel is open")

    def __exit__(self, exc_type, exc_value, traceback):
        self.tunnel.terminate()
        if exc_type is not None:
            print(exc_value, traceback)
            return False

class Validator:
    
    def __init__(self, config):
        self.ssh_address = config['validator_api']['ssh_address']
        self.keymanager_port = config['validator_api']['port']
        self.auth_token = config['validator_api']['auth_token']


    def load_keys(self, keystores, passwd):
        # get keys
        passwords = [passwd] * len(keystores)
        data = {
            'keystores': [json.dumps(x) for x in keystores],
            'passwords': passwords
        }
        url = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'

        # load validators into lighthouse
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'ContentType': 'application/json'
        }
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            # check if the keys are deployed
            response = requests.get(url=url, headers=headers)
            response_json = response.json()
            
            added_keylist = [k['validating_pubkey'] for k in response_json['data']]
            new_keylist= [f'0x{x["pubkey"]}' for x in keystores]
            
            if any([x in added_keylist for x in new_keylist]):
                raise Exception('The submitted keys are already loaded into the validator.')

            response = requests.post(url=url, headers=headers, json=data)
            if response.status_code != 200:
                raise Exception(f'Submission of keys to validator client unsuccessful. Status code: {response.status_code}')
            print(response.json(), flush=True) 
        
        if response.status_code == 200:
            print('Loaded keystores into validator successfuly')
        

    def remove_keys(self, keystores):
        
        pubkeys = [f'0x{x["pubkey"]}' for x in keystores]
        data = {
            'pubkeys': pubkeys
        }

        # load validators into lighthouse
        url = f'http://localhost:{self.keymanager_port}/eth/v1/keystores'
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'ContentType': 'application/json'
        }
        with SSHTunnel(self.ssh_address, self.keymanager_port):
            response = requests.delete(url=url, headers=headers, json=data)
            print(response.json(), flush=True) 
        if response.status_code != 200:
            raise Exception(f'while deleting keystores from validator: {response.status_code}')

        print('Deleted keystores from validator successfuly')



