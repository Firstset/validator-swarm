import os
from subprocess import CalledProcessError
import unittest
import unittest.mock as mock
import shutil
from swarm.deposit import Deposit

class TestDeposit(unittest.TestCase):
    def setUp(self):
        self.config = {
            'deposit': {
                'path': '/path/to/deposit',
                'withdrawal_address': '0xdeadbeef'
                },
            'chain': 'mainnet'
        }


    def test_deposit_correct_params(self):

        dep = Deposit(self.config)
        self.assertEqual(dep.chain, 'mainnet')
        self.assertEqual(dep.withdrawal, '0xdeadbeef')
        self.assertEqual(dep.path, '/path/to/deposit')
        
    def test_deposit_incorrect_params(self):
        with self.assertRaises(KeyError):
            Deposit({}) # missing config values


    # We assume that deposit-cli either creates correct files
    # and exits with exit code = 0, or does not create any
    # files and exits with exit code != 0
    @mock.patch('subprocess.check_output')
    def test_create_keys(self, mock_check_output):
        dep = Deposit(self.config)

        def copy_test_data(_):
            test_data_path = os.path.join(os.getcwd(), 'tests', 'test_data')
            target_path = os.path.join(os.getcwd(), 'validator_keys')
            
            shutil.copytree(test_data_path, target_path)
            
        mock_check_output.side_effect = copy_test_data
        keystores, deposit_data = dep.create_keys(1, 0, 'mnemo', 'pass')
        mock_check_output.assert_called()

        # check json files load successfully
        self.assertEqual('0xdeadbeef', keystores[0]['pubkey'])
        self.assertEqual('0xdeadbeef', deposit_data[0]['pubkey'])

        # check that files are removed
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), 'validator_keys')))


if __name__ == '__main__':
    unittest.main()
