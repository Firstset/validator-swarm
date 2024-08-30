from .protocol.csm import CSM
from .deposit import Deposit
from .validator import Validator
import sys
import toml
import getpass
import argparse

def read_mnemonic():
    mnemonic = input('Enter mnemonic: ')
    return mnemonic

def read_password():
    password = getpass.getpass('Enter password: ')
    return password

def main():
    parser = argparse.ArgumentParser(description='Validator key creation and submission')

    parser.add_argument('-n', '--n_keys', type=int, required=True, help='the number of keys to be created')
    parser.add_argument('-i', '--index', type=int, required=True, help='the starting key index')
    args = parser.parse_args(sys.argv[1:])

    if int(args.n_keys) <= 0 or int(args.index) < 0:
        parser.error('error while reading cli params')
    
    n = args.n_keys
    index = args.index
    
    try:
        config = toml.load("./config.toml")
    except Exception as e:
        sys.exit(f'Error: unable to open config.toml file. {e}')
    
    try:
        validator = Validator(config)
        deposit = Deposit(config)
        csm = CSM(config)
    except Exception as e:
        sys.exit(f'Error: while reading configuration file. {e}')

    try:
        mnemonic = read_mnemonic()
        passwd = read_password() 
    except Exception as e:
        sys.exit(f'Error: while reading password or mnemonic. {e}')

    try:
    # call ./deposit and create n validator keys
        keystores, deposit_data = deposit.create_keys(n, index, mnemonic, passwd)
    except Exception as e:
        sys.exit(f'Error: while creating deposit keys {e}')

    try:
        # submit keystores to validator client
        validator.load_keys(keystores, passwd)
        
    except Exception as e:
        sys.exit(f'Error: failed to load keys into validator client: {e}')

 
    try:
        # submit keys to protocol
        csm.submit_keys(deposit_data)
    except Exception as e:
        print(f'Error: failed to submit keys into protocol {e}')
        print('removing keys from validator client')
        # rollback 
        validator.remove_keys(keystores)


if __name__ == "__main__":
    main()
