import unittest
from unittest.mock import patch, Mock
from swarm import validator
from swarm.state_check import compute_state

class Args:
    def __init__(self):
        self.delete = False       

class TestDeposit(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'state_check': {
                'node_operator_ids': [1,2,3]
            }
        }
        self.args = Args()

    def test_check_only_csm(self):

        csm_keys = ['0xkey1', '0xkey2']
        validator_keys = []
        validator_remote_keys = []
        remote_signer_keys = []

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R5']), 2)
    
    def test_check_only_validator(self):

        csm_keys = []
        validator_keys = ['0xkey1', '0xkey2']
        validator_remote_keys = []
        remote_signer_keys = []

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R6']), 2)

    def test_check_only_remote_signer(self):

        csm_keys = []
        validator_keys = []
        validator_remote_keys = []
        remote_signer_keys = ['0xkey1', '0xkey2']

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R7']), 2)
    
    def test_check_csm_and_validator(self):

        csm_keys = ['0xkey1', '0xkey2']
        validator_keys = ['0xkey1', '0xkey2']
        validator_remote_keys = ['0xkey1']
        remote_signer_keys = []

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R2']), 2)
        self.assertEqual(len(state['R2_remote']), 1) 
        self.assertEqual(len(state['R2_local']), 1) 
    
    def test_check_csm_and_remote_signer(self):

        csm_keys = ['0xkey1', '0xkey2']
        validator_keys = []
        validator_remote_keys = []
        remote_signer_keys = ['0xkey1', '0xkey2']

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R3']), 2)
    
    def test_check_validator_and_remote_signer(self):

        csm_keys = []
        validator_keys = ['0xkey1', '0xkey2']
        validator_remote_keys = []
        remote_signer_keys = ['0xkey1', '0xkey2']

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R4']), 2)
    
    def test_check_csm_validator_and_remote_signer(self):

        csm_keys = ['0xkey1', '0xkey2']
        validator_keys = ['0xkey1', '0xkey2']
        validator_remote_keys = ['0xkey1']
        remote_signer_keys = ['0xkey1', '0xkey2']

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R1']), 2)
        self.assertEqual(len(state['R1_remote']), 1) 
        self.assertEqual(len(state['R1_local']), 1) 
    
    def test_check_all_regions(self):

        csm_keys = ['0xkey1', '0xkey4', '0xkey5', '0xkey7']
        validator_keys = ['0xkey2', '0xkey4', '0xkey6', '0xkey7']
        validator_remote_keys = ['0xkey4', '0xkey6']
        remote_signer_keys = ['0xkey3', '0xkey5', '0xkey6', '0xkey7']

        state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
        
        self.assertEqual(len(state['R1']), 1)
        self.assertEqual(len(state['R1_remote']), 0)
        self.assertEqual(len(state['R1_local']), 1)
        self.assertEqual(len(state['R2']), 1)
        self.assertEqual(len(state['R2_remote']), 1)
        self.assertEqual(len(state['R2_local']), 0)
        self.assertEqual(len(state['R3']), 1)
        self.assertEqual(len(state['R4']), 1)
        self.assertEqual(len(state['R5']), 1)
        self.assertEqual(len(state['R6']), 1)
        self.assertEqual(len(state['R7']), 1)
