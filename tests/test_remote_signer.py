import unittest
from unittest.mock import patch, Mock

from swarm.exception import ValidatorDeleteException, ValidatorLoadException
from swarm.validator import RemoteSigner

class TestRemoteSigner(unittest.TestCase):
    def setUp(self):
        self.config = {
            'remote_signer': {
                'url': '1.2.3.4:6666',
                'ssh_address': 'user@signer',
                'port': '4200',
                'auth_token': 'api-token-0xadeadbad'
            }
        }

    def test_validator_config_params(self):
        v = RemoteSigner(self.config)
        self.assertEqual(v.remote_signer_ssh_address, 'user@signer')
        self.assertEqual(v.remote_signer_port, '4200')

    def test_validator_missing_config_params(self):
        with self.assertRaises(KeyError):
            RemoteSigner({}) # missing config values
    
    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = RemoteSigner(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        v.load_keys(keystores, password)

        # implicit assert: no exceptions
        mock_get.assert_called_once()
        mock_post.assert_called_once()
    
    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_exists_in_signer(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = RemoteSigner(self.config)
        
        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'deadbeef'}]
        
        with self.assertRaises(ValidatorLoadException):
            v.load_keys(keystores, password)

    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_post_failed(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 400
        mock_post.return_value = post_response
        
        v = RemoteSigner(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        
        with self.assertRaises(ValidatorLoadException):
            v.load_keys(keystores, password)

    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 200
        mock_delete.return_value = delete_response
        
        v = RemoteSigner(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        v.remove_keys(keystores)

        # implicit assert: no exceptions
        mock_delete.assert_called_once()
    
    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys_fail(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 400
        mock_delete.return_value = delete_response
        
        v = RemoteSigner(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        with self.assertRaises(ValidatorDeleteException):
            v.remove_keys(keystores)

    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.get')
    def test_get_keys(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json = Mock()
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xthekey'}]}
        
        mock_get.return_value = get_response
        
        v = RemoteSigner(self.config)
        
        v.get_loaded_keys()

        # implicit assert: no exceptions
        mock_get.assert_called_once()
    
    @patch('swarm.validator.remote_signer.SSHTunnel')
    @patch('requests.get')
    def test_get_keys_fail(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 400
        
        mock_get.return_value = get_response
        
        v = RemoteSigner(self.config)
        
        with self.assertRaises(Exception):
            v.get_loaded_keys()

