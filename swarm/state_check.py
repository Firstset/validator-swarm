from swarm.exception import ValidatorDeleteException
from .protocol.csm import CSM
from .validator import Validator, RemoteSigner

warning = '⚠️'
ok = '✅'
critical = '🚨'

def print_state_summary(state):
    print()
    print('-------------------------------')
    print('VALIDATOR KEYS STATE SUMMARY:')
    print('-------------------------------')
    print(f'In CSM, Validator, and RemoteSigner: {len(state["R1"])}')
    print(f'\t Locally signed:  {len(state['R1_local'])} {warning if len(state['R1_local']) > 0 else ok}')
    print(f'\t Remotely signed: {len(state['R1_remote'])} {warning if len(state['R1_remote']) == 0 else ok}')
    print('-------------------------------')
    print('In CSM and Validator, but not in RemoteSigner:', len(state['R2']))
    print(f'\t Locally signed:  {len(state['R2_local'])} {warning if len(state['R2_local']) == 0 else ok}')
    print(f'\t Remotely signed: {len(state['R2_remote'])} {warning if len(state['R2_remote']) > 0 else ok}')
    print('-------------------------------')
    print(f'In CSM and RemoteSigner, but not in Validator: {len(state['R3'])} {critical if len(state['R3']) > 0 else ok}')
    print('-------------------------------')
    print(f'In Validator and RemoteSigner, but not in CSM: {len(state['R4'])} {warning if len(state['R4']) > 0 else ok}')
    print('-------------------------------')
    print(f'Only in CSM: {len(state['R5'])} {critical if len(state['R5']) > 0 else ok}')
    print('-------------------------------')
    print(f'Only in Validator: {len(state['R6'])} {warning if len(state['R6']) > 0 else ok}')
    print('-------------------------------')
    print(f'Only in RemoteSigner: {len(state['R7'])} {warning if len(state['R7']) > 0 else ok}')
    print('-------------------------------')

def compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys):
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

def delete_dangling(state, validator_remote_keys, remote_signer, validator):
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
        remote_signer.remove_keys(list(to_remove_from_signer))
        validator.remove_keys(list(to_remove_from_validator_local))
        validator.remove_remote_keys(list(to_remove_from_validator_remote))


async def do_check(config, args):
    delete = args.delete

    csm = CSM(config)
    validator = Validator(config)
    remote_signer = RemoteSigner(config)

    validator_keys = validator.get_loaded_keys()
    validator_remote_keys = validator.get_remote_keys()
    
    remote_signer_keys = remote_signer.get_loaded_keys()
    
    no_ids = config['monitoring']['node_operator_ids']
 
    csm_keys = [] 
    for id in no_ids:
        csm_keys += await csm.get_registered_keys(id)
    
    state = compute_state(csm_keys, validator_keys, validator_remote_keys, remote_signer_keys)
    print_state_summary(state)
    
    if delete:
        delete_dangling(state, validator_remote_keys, remote_signer, validator)

