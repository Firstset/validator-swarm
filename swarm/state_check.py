from argparse import Namespace
from typing import List

from eth_typing import Address
from swarm.exception import ValidatorDeleteException
from .protocol.csm import CSM
from .validator import Validator, RemoteSigner

warning = '⚠️'
ok = '✅'
critical = '🚨'

def print_state_summary(state) -> None:
    print()
    print('-------------------------------')
    print('VALIDATOR KEYS STATE SUMMARY:')
    print('-------------------------------')
    print(f'In CSM, Validator, and RemoteSigner: {len(state["R1"])}')
    print(f'\t Locally signed:  {len(state["R1_local"])} {warning if len(state["R1_local"]) > 0 else ok}')
    print(f'\t Remotely signed: {len(state["R1_remote"])} {warning if len(state["R1_remote"]) == 0 else ok}')
    print('-------------------------------')
    print('In CSM and Validator, but not in RemoteSigner:', len(state['R2']))
    print(f'\t Locally signed:  {len(state["R2_local"])} {warning if len(state["R2_local"]) == 0 else ok}')
    print(f'\t Remotely signed: {len(state["R2_remote"])} {warning if len(state["R2_remote"]) > 0 else ok}')
    if state["R2_remote"]:
        print("\t\tKeys:", ", ".join(str(k) for k in state["R2_remote"]))
    print('-------------------------------')
    print(f'In CSM and RemoteSigner, but not in Validator: {len(state["R3"])} {critical if len(state["R3"]) > 0 else ok}')
    if state["R3"]:
        print("\tKeys:", ", ".join(str(k) for k in state["R3"]))
    print('-------------------------------')
    print(f'In Validator and RemoteSigner, but not in CSM: {len(state["R4"])} {warning if len(state["R4"]) > 0 else ok}')
    if state["R4"]:
        print("\tKeys:", ", ".join(str(k) for k in state["R4"]))
    print('-------------------------------')
    print(f'Only in CSM: {len(state["R5"])} {critical if len(state["R5"]) > 0 else ok}')
    if state["R5"]:
        print("\tKeys:", ", ".join(str(k) for k in state["R5"]))
    print('-------------------------------')
    print(f'Only in Validator: {len(state["R6"])} {warning if len(state["R6"]) > 0 else ok}')
    if state["R6"]:
        print("\tKeys:", ", ".join(str(k) for k in state["R6"]))
    print('-------------------------------')
    print(f'Only in RemoteSigner: {len(state["R7"])} {warning if len(state["R7"]) > 0 else ok}')
    if state["R7"]:
        print("\tKeys:", ", ".join(str(k) for k in state["R7"]))
    print('-------------------------------')

def compute_state(
        csm_keys: List[Address], 
        validator_keys: List[Address], 
        validator_remote_keys: List[Address],
        remote_signer_keys: List[Address]
    ) -> dict:
    
    L = set(csm_keys)
    V = set(validator_keys)
    K = set(remote_signer_keys)
    
    R1 = L & V & K                  # In CSM, Validator, and RemoteSigner
    R2 = (L & V) - K                # In CSM and Validator, but not in RemoteSigner
    R3 = (L & K) - V                # In CSM and RemoteSigner, but not in Validator
    R4 = (V & K) - L                # In Validator and RemoteSigner, but not in CSM
    R5 = L - (V | K)                # Only in CSM
    R6 = V - (L | K)                # Only in Validator
    R7 = K - (L | V)                # Only in RemoteSigner
    
    R1_remote = R1 & set(validator_remote_keys) # Remotely signed keys in validator
    R1_local = R1 - R1_remote                       # Locally signed keys in validator

    R2_remote = R2 & set(validator_remote_keys) # Remotely signed keys in validator
    R2_local = R2 - R2_remote                   # Locally signed keys in validator
   
    state = {
        'R1': R1, 
        'R1_remote': R1_remote, 
        'R1_local': R1_local, 
        'R2': R2, 
        'R2_remote': R2_remote, 
        'R2_local': R2_local, 
        'R3': R3, 
        'R4': R4, 
        'R5': R5, 
        'R6': R6, 
        'R7': R7, 
    }
    return state

def delete_dangling(state: dict, validator_remote_keys: List[str], remote_signer: RemoteSigner, validator: Validator) -> None:
        to_remove_from_validator = state['R6'] | state['R4']
        to_remove_from_signer = state['R7'] | state['R4']

        print()
        print('-------------------------')
        print('STATE RECTIFICATION')
        print('-------------------------')
        print('Keys to remove from remote signer:')
        print('-------------------------')
        for k in to_remove_from_signer:
            print(k)
        print('-------------------------')
        print('Keys to remove from validator:')
        print('-------------------------')
        for k in to_remove_from_validator:
            print(k)
        
        to_remove_from_validator_remote = to_remove_from_validator & set(validator_remote_keys) #TODO: this info is already in state
        to_remove_from_validator_local = to_remove_from_validator - to_remove_from_validator_remote
        
        if len(to_remove_from_signer) > 0:
            remote_signer.remove_keys(list(to_remove_from_signer))
        if len(to_remove_from_validator_local) > 0:
            validator.remove_keys(list(to_remove_from_validator_local))
        if len(to_remove_from_validator_remote) > 0:
            validator.remove_remote_keys(list(to_remove_from_validator_remote))


async def do_check(config: dict, args: Namespace) -> None:
    delete = args.delete

    csm = CSM(config)
    validator = Validator(config)

    # Initialize remote_signer to None
    remote_signer = None

    # Check if remote signer is present in the config
    if 'remote_signer' in config:  # Check for remote signer configuration
        remote_signer = RemoteSigner(config)
        remote_signer_keys = remote_signer.get_loaded_keys()
    else:
        print("Remote signer not configured. Skipping related processing.")
        remote_signer_keys = []  # Set to empty if not present

    validator_keys = validator.get_loaded_keys()
    validator_remote_keys = validator.get_remote_keys()
    
    no_ids = config['monitoring']['node_operator_ids']
 
    csm_keys = [] 
    for id in no_ids:
        csm_keys += await csm.get_registered_keys(id)
    
    state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
    print_state_summary(state)
    
    if delete:  # Delete if the --delete flag is present, regardless of remote signer keys
        print("Deleting dangling keys...")
        delete_dangling(state, validator_remote_keys, remote_signer, validator)  # remote_signer can be None

