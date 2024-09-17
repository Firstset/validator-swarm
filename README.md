# Lido CSM validator manager

## Pre-requisites

- The [deposit key generation tool](https://github.com/ethereum/staking-deposit-cli)

- A previously generated seed phrase

- An execution layer RPC address
- A synchronized, running Ethereum node  (EL + CL)
    - An Ethereum account managed by the node, able to sign transactions.
- A running validator client with support for mutiple key management (e.g. Lighthouse)
    - With active Keymanager API listening in localhost
    - Reachable through ssh

## Setup

Copy `config.toml.example` to `config.toml` and fill with your configuration values

```
cp config.toml.example config.toml
```

The config file should contain:

```toml
# eth_base is the ETH address that will send the transaction 
# to register the Lido CSM validators. The bond will be send
# from eth_base's ETH balance
eth_base="<eth_base_address>" 
chain="holesky"

[deposit]
# Lido CSM testnet withdrawal address. 
withdrawal_address="0xF0179dEC45a37423EAD4FaD5fCb136197872EAd9"
path="/path/to/deposit/tool/deposit" # staking-cli-deposit executable

[csm]
# Lido CSM Node Operator id. Remove line if no ID has bee
# assigned yet.
node_operator_id=999999

[csm.contracts]
# Lido CSM tstnet contracts.
module_address="0x4562c3e63c2e586cD1651B958C22F88135aCAd4f"
accounting_address="0xc093e53e8F4b55A223c18A2Da6fA00e60DD5EFE1"

[rpc]
address="http://my-rpc-address:port"

[validator_api]
auth_token="api-token-0x123456789"
ssh_address="user@server"
port=5062

[remote_signer]
ssh_address="user@signer"
port=9000
url="http://my-signer.xyz:port"
```


Install python dependencies

```
pip install -r requirements.txt
```


## Exceute

`python -m swarm.main --n_keys <N> --index <I> [--remote_sign]`

`N` is the number of keys to be generated and submitted, and `I` is the starting index for key generation, defaults to 0.

The `--remote_sign` flag indicates that the keystores will be uploaded to a remote signer, while also registered as remote keys in the configured validator.

