import os
from subprocess import CalledProcessError
import unittest
from unittest.mock import patch, Mock
import shutil

from requests.api import get
from swarm.validator import Validator

class TestValidator(unittest.TestCase):
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
        self.assertEqual(v.auth_token, 'api-token-0xcafebabe')

    def test_validator_missing_config_params(self):
        with self.assertRaises(KeyError):
            Validator({}) # missing config values
    
    @patch('swarm.validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys(self, mock_post, mock_get, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = mock_ssh_tunnel.return_value 
        mock_ssh_tunnel_instance.__enter__.return_value = mock_ssh_tunnel
        mock_ssh_tunnel_instance.__exit__.return_value = False
        
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
    
    @patch('swarm.validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_key_exists(self, mock_post, mock_get, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = mock_ssh_tunnel.return_value 
        mock_ssh_tunnel_instance.__enter__.return_value = mock_ssh_tunnel
        mock_ssh_tunnel_instance.__exit__.return_value = False
        
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
        
        with self.assertRaises(Exception):
            v.load_keys(keystores, password)

        
    @patch('swarm.validator.SSHTunnel')
    @patch('requests.get')
    @patch('requests.post')
    def test_load_keys_post_failed(self, mock_post, mock_get, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = mock_ssh_tunnel.return_value 
        mock_ssh_tunnel_instance.__enter__.return_value = mock_ssh_tunnel
        mock_ssh_tunnel_instance.__exit__.return_value = False
        
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
        
        with self.assertRaises(Exception):
            v.load_keys(keystores, password)

    @patch('swarm.validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys(self, mock_delete, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = mock_ssh_tunnel.return_value 
        mock_ssh_tunnel_instance.__enter__.return_value = mock_ssh_tunnel
        mock_ssh_tunnel_instance.__exit__.return_value = False
        
        delete_response = Mock()
        delete_response.status_code = 200
        mock_delete.return_value = delete_response
        
        v = Validator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        v.remove_keys(keystores)

        # implicit assert: no exceptions
    
    @patch('swarm.validator.SSHTunnel')
    @patch('requests.delete')
    def test_remove_keys_fail(self, mock_delete, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = mock_ssh_tunnel.return_value 
        mock_ssh_tunnel_instance.__enter__.return_value = mock_ssh_tunnel
        mock_ssh_tunnel_instance.__exit__.return_value = False
        
        delete_response = Mock()
        delete_response.status_code = 400
        mock_delete.return_value = delete_response
        
        v = Validator(self.config)
        
        keystores = [{'pubkey': 'abadbabe'}]
        with self.assertRaises(Exception):
            v.remove_keys(keystores)

