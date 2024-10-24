from eth_typing import Address
import requests

from swarm.exception import ExitSignException, ExitBroadcastException, ConsensusLayerRPCException
from ..validator.ssh_tunnel import SSHTunnel
from ..util import is_well_formed_url

class ExitHandler():
    def __init__(self, config: dict) -> None:
        self.beacon_rpc = config['rpc']['consensus_address']
        if not is_well_formed_url(self.beacon_rpc, 'http'):
            raise ConsensusLayerRPCException('Consensus layer RPC is not well formed. It must be a valid http adress, and specify a port.')
        self.keymanager_ssh = config['validator_api']['ssh_address']
        self.keymanager_port = config['validator_api']['port']

        self.keymanager_headers = {
            'Authorization': f'Bearer {config["validator_api"]["auth_token"]}',
            'ContentType': 'application/json'
        }

        self.beacon_headers = {
            'ContentType': 'application/json'
        }

    def exit(self, pubkey: Address) -> None:
        # try local validator
        with SSHTunnel(self.keymanager_ssh, self.keymanager_port):
            url = f'http://localhost:{self.keymanager_port}/eth/v1/validator/{pubkey}/voluntary_exit'
            response = requests.post(url=url, headers=self.keymanager_headers)
            
            if response.status_code != 200:
                raise(ExitSignException('Could not sign validator exit message'))
            
            print('validator exit message signed succesfully')
            response_json = response.json()
            signed_exit_message = response_json['data']

        url = f'{self.beacon_rpc}/eth/v1/beacon/pool/voluntary_exits'
        data = signed_exit_message
        print('publishing validator exit message')
        response = requests.post(url=url, json=data, headers=self.beacon_headers)

        if response.status_code != 200:
            raise(ExitBroadcastException('Could not publish signed exit message'))

        print(f'published exit message for validator: {pubkey}')
