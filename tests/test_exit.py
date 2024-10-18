import unittest
from unittest.mock import patch, Mock
from swarm.validator.exit_handler import ExitHandler
from swarm.exception import ExitSignException, ExitBroadcastException

class Args:
    def __init__(self):
        self.pubkey = '0xdeadbeef'       

class TestDeposit(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'rpc': {
                'beacon_address': 'http://beacon-rpc.xyz:9090'
            },
            'validator_api': {
                'ssh_address': 'user@validator',
                'port': 666,
                'auth_token': 'the-token-123'
            }
        }
        self.args = Args()


    @patch('swarm.validator.exit_handler.SSHTunnel') 
    @patch('requests.post') 
    def test_exit(self, mock_post, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = Mock()
        mock_ssh_tunnel_instance.__enter__ = Mock ()
        mock_ssh_tunnel_instance.__exit__ = Mock ()
        mock_ssh_tunnel_instance.__exit__.return_value = False
        mock_ssh_tunnel.return_value = mock_ssh_tunnel_instance

        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = {
            'data':{
                'message': {
                    'epoch': 12345,
                    'validator_index': 54321
                },
                'signature': '0xcafebabe'
            }
        }

        mock_post.return_value = post_response


        handler = ExitHandler(self.config)
        handler.exit(self.args.pubkey)

        self.assertEqual(2, mock_post.call_count)


    @patch('swarm.validator.exit_handler.SSHTunnel') 
    @patch('requests.post') 
    def test_exit_sign_fail(self, mock_post, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = Mock()
        mock_ssh_tunnel_instance.__enter__ = Mock ()
        mock_ssh_tunnel_instance.__exit__ = Mock ()
        mock_ssh_tunnel_instance.__exit__.return_value = False
        mock_ssh_tunnel.return_value = mock_ssh_tunnel_instance

        post_response = Mock()
        post_response.status_code = 400

        mock_post.return_value = post_response


        handler = ExitHandler(self.config)
        with self.assertRaises(ExitSignException):
            handler.exit(self.args.pubkey)

    
    @patch('swarm.validator.exit_handler.SSHTunnel') 
    @patch('requests.post') 
    def test_exit_broadcast_fail(self, mock_post, mock_ssh_tunnel):
        mock_ssh_tunnel_instance = Mock()
        mock_ssh_tunnel_instance.__enter__ = Mock ()
        mock_ssh_tunnel_instance.__exit__ = Mock ()
        mock_ssh_tunnel_instance.__exit__.return_value = False
        mock_ssh_tunnel.return_value = mock_ssh_tunnel_instance

        post_response_1 = Mock()
        post_response_1.status_code = 200
        post_response_1.json.return_value = {
            'data':{
                'message': {
                    'epoch': 12345,
                    'validator_index': 54321
                },
                'signature': '0xcafebabe'
            }
        }

        post_response_2 = Mock()
        post_response_2.status_code = 400

        mock_post.side_effect = [post_response_1, post_response_2]


        handler = ExitHandler(self.config)
        with self.assertRaises(ExitBroadcastException):
            handler.exit(self.args.pubkey)

