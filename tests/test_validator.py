import unittest
from unittest.mock import patch, Mock

from swarm.validator import Validator
from swarm.exception import ValidatorLoadException, ValidatorDeleteException

class TestLocalValidator(unittest.TestCase):
    def setUp(self):
        self.config = {
            'validator_api': {
                'ssh_address': 'user@ip',
                'port': '42069',
                'auth_token': 'api-token-0xcafebabe'
                },
        }

    def test_validator_config_params(self):
        v = Validator(self.config)
        self.assertEqual(v.ssh_address, 'user@ip')
        self.assertEqual(v.keymanager_port, '42069')
        self.assertEqual(v.headers['Authorization'], 'Bearer api-token-0xcafebabe')

    def test_validator_missing_config_params(self):
        with self.assertRaises(KeyError):
            Validator({}) # missing config values
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys(self, mock_post, mock_get, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = Mock()
        mock_ssh_tunnel_instance.__enter__ = Mock ()
        mock_ssh_tunnel_instance.__exit__ = Mock ()
        mock_ssh_tunnel_instance.__exit__.return_value = False
        mock_ssh_tunnel.return_value = mock_ssh_tunnel_instance
        
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = Validator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        v.load_keys(keystores, password)

        # implicit assert: no exceptions

        mock_get.assert_called_once()
        mock_post.assert_called_once()
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_key_exists(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = Validator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'deadbeef'}]
        
        with self.assertRaises(ValidatorLoadException):
            v.load_keys(keystores, password)

        
    @patch('swarm.validator.validator.SSHTunnel')
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
        
        v = Validator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        
        with self.assertRaises(ValidatorLoadException):
            v.load_keys(keystores, password)

    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 200
        mock_delete.return_value = delete_response
        
        v = Validator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        v.remove_keys(keystores)

        # implicit assert: no exceptions
        mock_delete.assert_called_once()
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys_fail(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 400
        mock_delete.return_value = delete_response
        
        v = Validator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        with self.assertRaises(ValidatorDeleteException):
            v.remove_keys(keystores)

    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    def test_get_keys(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json = Mock()
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xthekey'}]}
        
        mock_get.return_value = get_response
        
        v = Validator(self.config)
        
        v.get_loaded_keys()

        # implicit assert: no exceptions
        mock_get.assert_called_once()
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    def test_get_keys_fail(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 400
        
        mock_get.return_value = get_response
        
        v = Validator(self.config)
        
        with self.assertRaises(Exception):
            v.get_loaded_keys()
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    def test_get_remote_keys(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json = Mock()
        get_response.json.return_value = {'data': [{'pubkey': '0xthekey'}]}
        
        mock_get.return_value = get_response
        
        v = Validator(self.config)
        
        v.get_remote_keys()

        # implicit assert: no exceptions
        mock_get.assert_called_once()
    
    @patch('swarm.validator.validator.SSHTunnel')
    @patch('requests.get')
    def test_get_keys_fail(self, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 400
        
        mock_get.return_value = get_response
        
        v = Validator(self.config)
        
        with self.assertRaises(Exception):
            v.get_remote_keys()
