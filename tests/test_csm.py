import unittest
import unittest.mock as mock
from swarm.protocol.csm import CSM
import copy
import swarm.util
import pytest
from swarm.exception import KeyExistsException

pytest_plugins = ('pytest_asyncio',)

config = {
    'csm': {
        'node_operator_id': 666,
        'contracts': {
            'module_address': '0xCSModule',
            'accounting_address': '0xAccounting',
            'VEBO_address': '0xVEBO'}
        },
    'rpc': {'execution_address': 'ws://my-rpc-provider:8546'},
    'eth_base': '0xabadbabe',
    'monitoring': {
        'node_operator_ids': [1, 2, 3, 420]
        }
    }

class TestCSM(unittest.TestCase):
    def setUp(self):
        self.config = config 

    def test_csm_correct_params(self):

        module = CSM(self.config)
        self.assertEqual(module.node_operator_id, 666)
        self.assertEqual(module.rpc, 'ws://my-rpc-provider:8546')
        self.assertEqual(module.eth_base, '0xabadbabe')

        names = ['module', 'accounting']
        for n in names:
            self.assertIsNotNone(module.contracts[n].get('abi'))
            self.assertIsNotNone(module.contracts[n].get('address'))

    def test_csm_incorrect_params(self):
        with self.assertRaises(KeyError):
            CSM({}) # missing config values

    

@mock.patch('swarm.protocol.csm.local_sign', autospec=True)
@mock.patch('swarm.protocol.csm.CSM.have_repeated_keys', autospec=True)
@mock.patch('swarm.protocol.csm.NodeWSConnection', autospec=True)
@mock.patch('swarm.protocol.csm.CSM.get_eth_bond', autospec=True)
@pytest.mark.asyncio
async def test_submit_keys(mock_get_bond, mock_node_connection_class, mock_repeated_keys, mock_local_sign):
    mock_get_bond.return_value = 2
    mock_local_sign.return_value = '0xtxhash'
    
    # Set up contract call mocks
    add_val_existing_no_instance = mock.Mock()
    add_val_existing_no_instance.build_transaction = mock.AsyncMock()
    add_val_existing_no_instance.build_transaction.return_value = {'mock': 'tx'}
    add_val_existing_no = mock.Mock()
    add_val_existing_no.return_value = add_val_existing_no_instance

    add_val_new_no_instance = mock.Mock()
    add_val_new_no_instance.build_transaction = mock.AsyncMock()
    add_val_new_no_instance.build_transaction.return_value = {'mock': 'tx'}
    add_val_new_no = mock.Mock()
    add_val_new_no.return_value = add_val_new_no_instance

    contract_mock = mock.Mock()
    contract_mock.functions = {
        'addNodeOperatorETH': add_val_new_no,
        'addValidatorKeysETH': add_val_existing_no,
    }

    syncMock = mock.Mock()
    syncMock.get_contract.return_value = contract_mock

    connection_instance_mock = mock.AsyncMock()
    connection_instance_mock.__aenter__.return_value = syncMock

    mock_node_connection_class.return_value = connection_instance_mock

    mock_repeated_keys.return_value = False

    module = CSM(config)
    await module.submit_keys_local_sign([
        {'pubkey': '0x0', 'signature': '0x3'},
        {'pubkey': '0x1', 'signature': '0x4'}
    ])

    add_val_existing_no.assert_called_once_with(
        666,
        2,
        b'\x00\x01',
        b'\x03\x04',
    )

    add_val_existing_no_instance.build_transaction.assert_called_once_with({
        'value': '0x2',
        'from': '0xabadbabe'
    })
    
    mock_local_sign.assert_called_with(8000, {'mock': 'tx'})

    # Test for new node operator
    new_config = copy.deepcopy(config)
    del new_config['csm']['node_operator_id']
    module = CSM(new_config)
    await module.submit_keys_local_sign([
        {'pubkey': '0x5', 'signature': '0x6'},
        {'pubkey': '0x7', 'signature': '0x8'}
    ])

    add_val_new_no.assert_called_once_with(
        2,
        b'\x05\x07',
        b'\x06\x08',
        (swarm.util.int_to_address(0), swarm.util.int_to_address(0), False),
        [],
        swarm.util.int_to_address(0)
    )

    add_val_new_no_instance.build_transaction.assert_called_once_with({
        'value': '0x2',
        'from': '0xabadbabe'
    })

    mock_local_sign.assert_called_with(8000, {'mock': 'tx'})

@mock.patch('swarm.protocol.csm.CSM.have_repeated_keys', autospec=True)
@pytest.mark.asyncio
async def test_submit_keys_repeated(mock_repeated_keys):
    mock_repeated_keys.return_value = True

    module = CSM(config)
    with pytest.raises(KeyExistsException):
        await module.submit_keys_local_sign([
            {'pubkey': '0x0', 'signature': '0x3'},
            {'pubkey': '0x1', 'signature': '0x4'}
        ])


@pytest.mark.asyncio
@mock.patch('swarm.protocol.csm.NodeWSConnection')
async def test_get_bond(mock_node_connection_class):
    get_bond_existing_no_instance = mock.Mock()
    get_bond_existing_no_instance.call = mock.AsyncMock()
    get_bond_existing_no_instance.call.return_value = 2
    get_bond_existing_no = mock.Mock()
    get_bond_existing_no.return_value = get_bond_existing_no_instance

    get_bond_new_no_instance = mock.Mock()
    get_bond_new_no_instance.call = mock.AsyncMock()
    get_bond_new_no_instance.call.return_value = 2
    get_bond_new_no = mock.Mock()
    get_bond_new_no.return_value = get_bond_new_no_instance

    contract_mock = mock.Mock()
    contract_mock.functions = {
        'getBondAmountByKeysCount': get_bond_new_no,
        'getRequiredBondForNextKeys': get_bond_existing_no,
    }

    syncMock = mock.Mock()
    syncMock.get_contract.return_value = contract_mock

    connection_instance_mock = mock.AsyncMock()
    connection_instance_mock.__aenter__.return_value = syncMock

    mock_node_connection_class.return_value = connection_instance_mock

    # test correct contract function called when node operator
    # id is provided

    module = CSM(config)
    await module.get_eth_bond(4)

    get_bond_existing_no.assert_called_once_with(666, 4)
    get_bond_existing_no_instance.call.assert_called_once()


    # test correct contract function called when node operator
    # id is not provided

    new_config = copy.deepcopy(config)
    del new_config['csm']['node_operator_id']
    module = CSM(new_config)
    await module.get_eth_bond(4)

    get_bond_new_no.assert_called_once_with(4, 0)
    get_bond_new_no_instance.call.assert_called_once()
