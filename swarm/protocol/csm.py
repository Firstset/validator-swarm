import requests
from .. import util
import os
from web3 import Web3, exceptions
from ..connection.connection import NodeWSConnection
from ..exception import CSMSubmissionException, KeyExistsException, TransactionRejectedException, ExecutionLayerRPCException
from ..local_sign import local_sign

class CSM:
    def __init__(self, config):

        cwd = os.getcwd()
        self.node_operator_id = config['csm'].get('node_operator_id') # None if not present
        self.rpc = config['rpc']['execution_address']
        if not util.is_well_formed_url(self.rpc, 'ws'):
            raise ExecutionLayerRPCException('Excecution layer RPC is not well formed. It must be a valid web socket address, and specify a port.')

        self.eth_base = config['eth_base']

        contract_names = [
            'module',
            'accounting',
            'VEBO'
        ]

        self.contracts = {}

        for name in contract_names:
            self.contracts[name] = {}
            self.contracts[name]['abi'] = util.load_abi(os.path.join(cwd, 'abis', 'csm', f'{name}.json'))
            self.contracts[name]['address'] = config['csm']['contracts'][f'{name}_address']

        self.exit_monitor_ids = config['monitoring']['node_operator_ids']

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
        
    async def get_registered_keys(self, id):
        print(f'Fetching all keys registered in CSM {id}...')
        async with NodeWSConnection(self.rpc) as con:
            contract = con.get_contract(**self.contracts['module'])
            function = contract.functions['getNodeOperator']
            summary = await function(id).call()
            total_added_keys = summary[0]

            function = contract.functions['getSigningKeys']
            res = await function(id, 0, total_added_keys).call()
            keys = Web3.to_hex(res)[2:]
            split = [keys[i:i+96] for i in range(0, len(keys), 96)]
        return [f'0x{k}' for k in split]

    async def get_eth_bond(self, n_validators):
        async with NodeWSConnection(self.rpc) as con:
            print(con)
            contract = con.get_contract(**self.contracts['accounting']) 
            if self.node_operator_id == None:
                function = contract.functions['getBondAmountByKeysCount']
                bond = await function(n_validators, 0).call()
            else:
                function = contract.functions['getRequiredBondForNextKeys']
                bond = await function(self.node_operator_id, n_validators).call()
            
            print(f'Bond is {bond/(1e18)} ETH for {n_validators} keys')
        return bond

    async def submit_keys(self, deposit_data):

        if self.have_repeated_keys(deposit_data):
            print("Error: one or more keys are already uploaded to the protocol")
            raise KeyExistsException()

        bond = await self.get_eth_bond(len(deposit_data))
        
        print('Submitting keys....')
        async with NodeWSConnection(self.rpc) as con:
            contract = con.get_contract(**self.contracts['module'])
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
                resp = await contract_call.transact(tx)
                print('Tx hash: ', Web3.to_hex(resp))

            except exceptions.ContractCustomError as e:
                print(e.data)
                print('Exception', e.message)
                raise e
            
        print('Uploaded keys and sent ETH to CSM sucessfully')

    async def submit_keys_local_sign(self, deposit_data):

        if self.have_repeated_keys(deposit_data):
            print("Error: one or more keys are already uploaded to the protocol")
            raise KeyExistsException()

        bond = await self.get_eth_bond(len(deposit_data))
        
        print('Submitting keys....')

        async with NodeWSConnection(self.rpc) as con:
            contract = con.get_contract(**self.contracts['module'])
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
            tx = {'value': hex(bond), 'from': self.eth_base}
            try:
                complete_tx = await contract_call.build_transaction(tx)
                resp = await local_sign(8000, complete_tx)
                print('Tx hash: ', resp)

            except exceptions.ContractCustomError as e:
                print(e.data)
                print('Error returnerd by contract call', e.message)
                raise CSMSubmissionException(e)
            except TransactionRejectedException as e:
                print('Transaction was rejected by signer.')
                raise CSMSubmissionException(e)
        
        print('Uploaded keys and sent ETH to CSM sucessfully')
    async def exit_monitor(self):
        async with NodeWSConnection(self.rpc) as con:
            contract = con.get_contract(**self.contracts['VEBO'])
            event = contract.events['ValidatorExitRequest']
            filter = await event.create_filter(
                    from_block='latest',
                    argument_filters = {
                        'stakingModuleId': 4, # Harcoded CSM module id
                        'nodeOperatorId': self.exit_monitor_ids, 
                    })
            await con.w3.eth.subscribe('newHeads')
            async for _ in con.w3.socket.process_subscriptions():
                print('Checking for exit request events...')
                for e in await filter.get_new_entries():
                    yield e
