from pathlib import Path
import subprocess
import os
import shutil
import json

from .exception import DepositException
from .util import is_file_executable

class Deposit:
    def __init__(self, config):
        self.path = config['deposit']['path'] 
        self.withdrawal = config['deposit']['withdrawal_address']
        self.chain = config['chain']
        
        if not is_file_executable(self.path):
            raise DepositException('deposit-cli executable cannot be found.')
       

    def create_keys(self, n_keys: int, index: int, mnemonic: str, password: str):
        try:
            print(f'creating {n_keys} keys...')
            subprocess.check_output([
                self.path, 
                '--non_interactive',
                '--language',
                'english',
                'existing-mnemonic',
                '--num_validators',
                str(n_keys),
                '--validator_start_index',
                str(index),
                '--chain',
                self.chain,
                '--eth1_withdrawal_address',
                self.withdrawal,
                '--mnemonic',
                mnemonic,
                '--keystore_password',
                password])
            print('Success!')
            
            # Get and parse deposit file
            directory = Path(os.path.join(os.getcwd(), 'validator_keys'))

            all_deposit_files = [f for f in directory.iterdir() if f.is_file() and f.name.endswith('.json') and f.name.startswith('deposit_data')]
            all_deposit_files.sort()

            deposit_file = all_deposit_files[-1]
            #keystores = files
            with open(deposit_file, 'r') as f:
                deposit_data = json.load(f)

            
            all_keystore_files = [f for f in directory.iterdir() if f.is_file() and f.name.endswith('.json') and f.name.startswith('keystore')]
            all_keystore_files = sorted(all_keystore_files, key=lambda p: p.stat().st_ctime)

            keystores = []
            keystore_files = all_keystore_files[-n_keys:]
            for kf in keystore_files:
                with open(kf, 'r') as f:
                    keystores.append(json.load(f))
            
            # remove kystore and deposit data files
            # os.remove(directory) ?
            shutil.rmtree(directory)
        except Exception as ex:
            raise DepositException(ex)
        return keystores, deposit_data
