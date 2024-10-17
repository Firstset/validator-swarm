from .protocol.csm import CSM
from .deposit import Deposit
from .validator import Validator, RemoteSigner 
from .exception import * 
import sys
import secrets

def read_mnemonic():
    mnemonic = input('Enter mnemonic: ')
    return mnemonic

def read_password():
    password = secrets.token_bytes(8).hex() 
    return password

async def deploy(config, args):
    if args.n_keys <= 0 or args.index < 0:
        sys.exit('incorrect parameters for validator key deployment')
    
    n = args.n_keys
    index = args.index
    remote = args.remote_sign

    try:
        remote_signer = RemoteSigner(config) if remote else None
        validator = Validator(config)
        deposit = Deposit(config)
        csm = CSM(config)
    except ConfigException as e:
        sys.exit(f'Error: while reading configuration file. {e}')

    try:
        mnemonic = read_mnemonic()
        passwd = read_password() 
    except InputException as e:
        sys.exit(f'Error: while reading password or mnemonic. {e}')

    try:
    # call ./deposit and create n validator keys
        keystores, deposit_data = deposit.create_keys(n, index, mnemonic, passwd)
    except DepositException as e:
        sys.exit(f'Error: while creating deposit keys {e}')

    try:
        if remote and remote_signer != None:
            remote_signer.load_keys(keystores, passwd)
            validator.load_remote_keys(keystores, remote_signer.remote_signer_url)
        else:
            # submit keystores to validator client
            validator.load_keys(keystores, passwd)
        
    except ValidatorLoadException as e:
        sys.exit(f'Error: failed to load keys into validator client: {e}')

 
    try:
        # submit keys to protocol
        # await csm.submit_keys(deposit_data)
        await csm.submit_keys_local_sign(deposit_data)
    except CSMSubmissionException as e:
        sys.exit(f'Error: failed to submit keys into protocol {e}')
