import requests
from .. import util
import os
from web3 import Web3, exceptions
from collections import defaultdict

class CSM:
    def __init__(self, config):

        cwd = os.getcwd()
        self.node_operator_id = config['csm'].get('node_operator_id') # None if not present
        self.rpc = config['rpc']['execution_address']
        self.eth_base = config['eth_base']

        contract_names = [
            'module',
            'accounting'
        ]

        self.contracts = {}

        for name in contract_names:
            self.contracts[name] = {}
            self.contracts[name]['abi'] = util.load_abi(os.path.join(cwd, 'abis', 'csm', f'{name}.json'))
            self.contracts[name]['address'] = config['csm']['contracts'][f'{name}_address']

# TODO: decouple
    def get_contract(self, name):
        con = Web3(Web3.HTTPProvider(self.rpc, request_kwargs={'timeout': 60}))
        contract = con.eth.contract(
            address=self.contracts[name]['address'],
            abi=self.contracts[name]['abi'])
        return contract

    def have_repeated_keys(self, deposit_data):
        pubkeys = [x['pubkey'] for x in deposit_data]
        url = f'https://keys-api-holesky.testnet.fi/v1/keys/find'
        headers = {
            'ContentType': 'application/json'
        }

        data = {
            'pubkeys': pubkeys
        }
        
        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        return len(response_json['data']) > 0
        
    def get_registered_keys(self, id):
        print(f'Fetching all keys registered in CSM {id}...')
        contract = self.get_contract('module')
        function = contract.functions['getNodeOperator']
        summary = function(id).call()
        total_added_keys = summary[0]

        function = contract.functions['getSigningKeys']
        res = function(id, 0, total_added_keys).call()
        keys = Web3.to_hex(res)[2:]
        split = [keys[i:i+96] for i in range(0, len(keys), 96)]
        return [f'0x{k}' for k in split]

    def get_eth_bond(self, n_validators):
        contract = self.get_contract('accounting') 
        if self.node_operator_id == None:
            function = contract.functions['getBondAmountByKeysCount']
            bond = function(n_validators, 0).call()
        else:
            function = contract.functions['getRequiredBondForNextKeys']
            bond = function(self.node_operator_id, n_validators).call()
        
        print(f'Bond is {bond/(1e18)} ETH for {n_validators} keys')
        return bond

    def submit_keys(self, deposit_data):

        if self.have_repeated_keys(deposit_data):
            print("Error: one or more keys are already uploaded to the protocol")
            exit(-1)

        bond = self.get_eth_bond(len(deposit_data))
        
        print('Submitting keys....')
        contract = self.get_contract('module')
        pubkeys = [Web3.to_bytes(hexstr=(x['pubkey'])) for x in deposit_data]
        pubkeys_bytes = b''.join(pubkeys)
        sigs = [Web3.to_bytes(hexstr=(x['signature'])) for x in deposit_data]
        sigs_bytes = b''.join(sigs)
        management = (util.int_to_address(0), util.int_to_address(0), False)
        referrer =  util.int_to_address(0)
        if self.node_operator_id == None:
            function = contract.functions['addNodeOperatorETH']
            contract_call = function(
                len(deposit_data), 
                pubkeys_bytes,
                sigs_bytes,
                management, 
                [],
                referrer
            )
        else:
            function = contract.functions['addValidatorKeysETH']
            contract_call = function(
                self.node_operator_id,
                len(deposit_data), 
                pubkeys_bytes,
                sigs_bytes
            )
        tx = {
            'value': bond,
            'from': self.eth_base,
            'to': self.contracts['module']['address'],
            }
        try:
            # resp = contract_call.transact(tx)
            resp = contract_call.transact(tx)
            print('Tx hash: ', Web3.to_hex(resp))

        except exceptions.ContractCustomError as e:
            print(e.data)
            print('Exception', e.message)
            exit(-1)
        
        print('Uploaded keys and sent ETH to CSM sucessfully')
