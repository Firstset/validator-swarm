import unittest
from unittest.mock import patch, Mock

from swarm.validator import RemoteValidator

class TestRemoteValidator(unittest.TestCase):
    def setUp(self):
        self.config = {
            'remote_signer': {
                'url': '1.2.3.4:6666',
                'ssh_address': 'user@signer',
                'port': '69420',
                'auth_token': 'api-token-0xadeadbad'
            },
            'validator_api': {
                'ssh_address': 'user@ip',
                'port': '42069',
                'auth_token': 'api-token-0xcafebabe'
            }
        }

    def test_validator_config_params(self):
        v = RemoteValidator(self.config)
        self.assertEqual(v.ssh_address, 'user@ip')
        self.assertEqual(v.keymanager_port, '42069')
        self.assertEqual(v.auth_token, 'api-token-0xcafebabe')

    def test_validator_missing_config_params(self):
        with self.assertRaises(KeyError):
            RemoteValidator({}) # missing config values
    
    @patch('swarm.validator.remote_validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_to_remote_signer(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'validating_pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = RemoteValidator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        v.load_keys_to_remote_signer(keystores, password)

        # implicit assert: no exceptions

    @patch('swarm.validator.remote_validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_remote_keys_to_validator(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = RemoteValidator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        v.load_remote_keys_to_validator_client(keystores)

        # implicit assert: no exceptions
    
    @patch('swarm.validator.remote_validator.SSHTunnel')
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
        
        v = RemoteValidator(self.config)
        
        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'deadbeef'}]
        
        with self.assertRaises(Exception):
            v.load_keys_to_remote_signer(keystores, password)

    @patch('swarm.validator.remote_validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_remote_exists_in_validator(self, mock_post, mock_get, mock_ssh_tunnel):
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {'data': [{'pubkey': '0xdeadbeef'}]} 
        mock_get.return_value = get_response

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = [{'status': 'imported'}]
        mock_post.return_value = post_response
        
        v = RemoteValidator(self.config)

        keystores = [{'pubkey': 'deadbeef'}]
        
        with self.assertRaises(Exception):
            v.load_remote_keys_to_validator_client(keystores)
        
    @patch('swarm.validator.remote_validator.SSHTunnel')
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
        
        v = RemoteValidator(self.config)
        

        password = 'p4$$w0rd'
        keystores = [{'pubkey': 'abadbabe'}]
        
        with self.assertRaises(Exception):
            v.load_keys_to_remote_signer(keystores, password)


        get_response.json.return_value = {'data': [{'pubkey': '0xdeadbeef'}]} 
        with self.assertRaises(Exception):
            v.load_remote_keys_to_validator_client(keystores)

    @patch('swarm.validator.remote_validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 200
        mock_delete.return_value = delete_response
        
        v = RemoteValidator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        v.remove_keys_from_remote_signer(keystores)
        v.remove_remote_keys_from_validator_client(keystores)

        # implicit assert: no exceptions
    
    @patch('swarm.validator.remote_validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys_fail(self, mock_delete, mock_ssh_tunnel):
        delete_response = Mock()
        delete_response.status_code = 400
        mock_delete.return_value = delete_response
        
        v = RemoteValidator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        with self.assertRaises(Exception):
            v.remove_keys_from_remote_signer(keystores)

        with self.assertRaises(Exception):
            v.remove_remote_keys_from_validator_client(keystores)

