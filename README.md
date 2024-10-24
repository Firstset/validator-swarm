# Lido CSM validator manager

A CLI tool to deploy, monitor and manage validator keys for the Lido CSM.

## Features

- Deploy validators: Create and deploy new validator keys to the validator client and CSM
- Manage validator keys: 
  - Find inconsistencies between generated keys, loaded keystores and successfully registered validators
  - Rollback inconsistent states
- Exit validators:
  - Manually, with its public key
  - Automatically, by monitoring the Lido Validator Exit Bus Oracle and actioning exit requests
- Support for remote signer setups (e.g. web3signer)

## Pre-requisites

- The [deposit key generation tool](https://github.com/ethereum/staking-deposit-cli)
- A previously generated seed phrase
- Access to a synchronized, running Ethereum RPC node (EL & CL)
  - Reachable through HTTP & WS (CL & EL respectively)
- A running validator client with support for mutiple key management (e.g. Lighthouse)
  - With active Keymanager API listening in localhost
  - Reachable through SSH

## Setup

Copy `config.toml.holesky.example` or `config.toml.mainnet.example` to `config.toml` and fill with your configuration values

```
cp config.toml.holesky.example config.toml
```

The Holesky config file may contain:

```toml
eth_base=<eth_base_address>
chain="holesky"

[deposit]
withdrawal_address=<withdrawal_address>
path="/path/to/deposit/tool/deposit/"

[csm]
node_operator_id=999999

[csm.contracts]
module_address="0x4562c3e63c2e586cD1651B958C22F88135aCAd4f"
accounting_address="0xc093e53e8F4b55A223c18A2Da6fA00e60DD5EFE1"
VEBO_address="0xffDDF7025410412deaa05E3E1cE68FE53208afcb"

[rpc]
execution_address="ws://my-exec-rpc-address:port"
consensus_address="http://my-beacon-rpc-address:port"

[validator_api]
auth_token="api-token-0x123456789"
ssh_address="user@server"
port=5062

[remote_signer]
ssh_address="user@signer"
port=9000
url="http://my-remote-signer.xyz:port"

[monitoring]
node_operator_ids = [420, 666]
```

Some of these parameters are optional and can be omitted depending on the functionality you want to use.


Install python dependencies

```
pip install -r requirements.txt
```


## Execute

### Deploy validators 

`python -m swarm deploy --n_keys <N> --index <I> [--remote_sign]`

`N` is the number of keys to be generated and submitted, and `I` is the starting index for key generation, defaults to 0.

The `--remote_sign` flag indicates that the keystores will be uploaded to a remote signer, while also registered as remote keys in the configured validator. Otherwise, the keystores will be stored in the validator client.

### State check

The state check subcommand will retrieve all keys registered in CSM, validator client, and remote signer, and check for inconsistencies.

`python -m swarm state-check [--delete]`

`--delete` will attempt to remove dangling validator keys, i.e. validator keys that are present either in the validaor client or remote signer, but not in CSM. Keys registered in CSM will never be deleted.

### Manual exit

This subcommand will submit an exit request for a validator with a given public key.

`python -m swarm exit --pubkey <pubkey>`

`pubkey` is the public key of the validator to be exited.

### Monitoring and automated exits

This subcommand will monitor the Lido Validator Exit Bus Oracle and log exit requests for the configured node operator ids.

`python -m swarm auto_exit [--delete]`

The `--delete` flag indicates that the validator will be automatically exited when an exit request has been detected.
