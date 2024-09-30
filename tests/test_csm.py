import unittest
import unittest.mock as mock
from swarm.protocol.csm import CSM
import copy
import swarm.util

class TestCSM(unittest.TestCase):
    def setUp(self):
        self.config = {
            'csm': {
                'node_operator_id': 666,
                'contracts': {
                    'module_address': '0xCSModule',
                    'accounting_address': '0xAccounting'}
                },
            'rpc': {'execution_address': 'http://my-rpc-provider:8545'},
            'eth_base': '0xabadbabe'
            }


    def test_csm_correct_params(self):

        module = CSM(self.config)
        self.assertEqual(module.node_operator_id, 666)
        self.assertEqual(module.rpc, 'http://my-rpc-provider:8545')
        self.assertEqual(module.eth_base, '0xabadbabe')

        names = ['module', 'accounting']
        for n in names:
            self.assertIsNotNone(module.contracts[n].get('abi'))
            self.assertIsNotNone(module.contracts[n].get('address'))

    def test_csm_incorrect_params(self):
        with self.assertRaises(KeyError):
            CSM({}) # missing config values

    

    @mock.patch('swarm.protocol.csm.CSM.get_contract')
    def test_get_bond(self, mock_get_contract):
        get_bond_existing_no_instance = mock.Mock()
        get_bond_existing_no_instance.call = mock.Mock()
        get_bond_existing_no_instance.call.return_value = 2
        get_bond_existing_no = mock.Mock()
        get_bond_existing_no.return_value = get_bond_existing_no_instance

        get_bond_new_no_instance = mock.Mock()
        get_bond_new_no_instance.call = mock.Mock()
        get_bond_new_no_instance.call.return_value = 2
        get_bond_new_no = mock.Mock()
        get_bond_new_no.return_value = get_bond_new_no_instance

        contract_mock = mock.Mock()
        contract_mock.functions = {
            'getBondAmountByKeysCount': get_bond_new_no,
            'getRequiredBondForNextKeys': get_bond_existing_no,
        }

        mock_get_contract.return_value = contract_mock

        # test correct contract function called when node operator
        # id is provided

        module = CSM(self.config)
        module.get_eth_bond(4)

        get_bond_existing_no.assert_called_once_with(666, 4)
        get_bond_existing_no_instance.call.assert_called_once()


        # test correct contract function called when node operator
        # id is not provided

        new_config = copy.deepcopy(self.config)
        del new_config['csm']['node_operator_id']
        module = CSM(new_config)
        module.get_eth_bond(4)

        get_bond_new_no.assert_called_once_with(4, 0)
        get_bond_new_no_instance.call.assert_called_once()

    @mock.patch('swarm.protocol.csm.CSM.get_contract')
    @mock.patch('swarm.protocol.csm.CSM.get_eth_bond')
    def test_submit_keys(self, mock_get_bond, mock_get_contract):
        mock_get_bond.return_value = 2.0
        
        add_val_existing_no_instance = mock.Mock()
        add_val_existing_no_instance.transact = mock.Mock()
        add_val_existing_no_instance.transact.return_value = b'abcd'
        add_val_existing_no = mock.Mock()
        add_val_existing_no.return_value = add_val_existing_no_instance

        add_val_new_no_instance = mock.Mock()
        add_val_new_no_instance.transact = mock.Mock()
        add_val_new_no_instance.transact.return_value = b'abcd'
        add_val_new_no = mock.Mock()
        add_val_new_no.return_value = add_val_new_no_instance

        contract_mock = mock.Mock()
        contract_mock.functions = {
            'addNodeOperatorETH': add_val_new_no,
            'addValidatorKeysETH': add_val_existing_no,
        }

        mock_get_contract.return_value = contract_mock


        module = CSM(self.config)
        module.submit_keys([
            {'pubkey': '0x0', 'signature': '0x3'},
            {'pubkey': '0x1', 'signature': '0x4'}
        ])

        add_val_existing_no.assert_called_once_with(
            666,
            2,
            b'\x00\x01',
            b'\x03\x04',
        )

        add_val_existing_no_instance.transact.assert_called_once_with({
            'value': 2.0,
            'from': '0xabadbabe',
            'to': '0xCSModule'
        })
        
        new_config = copy.deepcopy(self.config)
        del new_config['csm']['node_operator_id']
        module = CSM(new_config)
        module.submit_keys([
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

        add_val_new_no_instance.transact.assert_called_once_with({
            'value': 2.0,
            'from': '0xabadbabe',
            'to': '0xCSModule'
        })

