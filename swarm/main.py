from swarm.validator.remote_validator import RemoteValidator
from .protocol.csm import CSM
from .deposit import Deposit
from .validator import RemoteValidator, LocalValidator 
from .exception import * 
import sys
import toml
import argparse
import secrets

def read_mnemonic():
    mnemonic = input('Enter mnemonic: ')
    return mnemonic

def read_password():
    password = secrets.token_bytes(8).hex() 
    
    return password

def main():
    parser = argparse.ArgumentParser(description='Validator key creation and submission')

    parser.add_argument('-n', '--n_keys', type=int, required=True, help='the number of keys to be created')
    parser.add_argument('-i', '--index', type=int, default=0, help='the starting key index')
    parser.add_argument('-r', '--remote_sign', type=bool, default=False, help='if true, validators will be configured with remote signing')
    args = parser.parse_args(sys.argv[1:])

    if int(args.n_keys) <= 0 or int(args.index) < 0:
        parser.error('error while reading cli params')
    
    n = args.n_keys
    index = args.index
    remote = args.remote_sign

    try:
        config = toml.load("./config.toml")
    except Exception as e:
        sys.exit(f'Error: unable to open config.toml file. {e}')
    
    try:
        if remote:
            validator = RemoteValidator(config)
        else:
            validator = LocalValidator(config)
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
        # submit keystores to validator client
        validator.load_keys(keystores, passwd)
        
    except ValidatorLoadException as e:
        sys.exit(f'Error: failed to load keys into validator client: {e}')

 
    try:
        # submit keys to protocol
        csm.submit_keys(deposit_data)
    except CSMSubmissionException as e:
        print(f'Error: failed to submit keys into protocol {e}')
        print('removing keys from validator client')
        # rollback 
        validator.remove_keys(keystores)


if __name__ == "__main__":
    main()
