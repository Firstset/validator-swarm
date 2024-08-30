# Lido CSM one-shot validator spawning

## Requirements

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

The following table details the fields required by the config file:

| **Section**            | **Key**               | **Value**                                     | **Description**                                                      |
|------------------------|-----------------------|-----------------------------------------------|----------------------------------------------------------------------|
| *Root*                 | `eth_base`            | `<eth_base_address>`                          | Ethereum address that will provide bond funds, and sign transaction  |
| *Root*                 | `chain`               | `"holesky"`                                   | Name of the ethereum network (e.g. holesky, mainnet)                 |
| **[deposit]**          | `withdrawal_address`  | `<withdrawal_address>`                        | Address to set as withdraw address of the validator                  |
| **[deposit]**          | `path`                | `"/path/to/deposit/tool/deposit/"`            | Path to the deposit tool                                             |
| **[csm]**              | `node_operator_id`    | `999999`                                      | Node operator identifier                                             |
| **[csm.contracts]**    | `module_address`      | `"0x4562c3e63c2e586cD1651B958C22F88135aCAd4f"`| Lido Community Staking Module contract address                       |
| **[csm.contracts]**    | `accounting_address`  | `"0xc093e53e8F4b55A223c18A2Da6fA00e60DD5EFE1"`| Lido Community Staking Module Accounting contract address            |
| **[rpc]**              | `address`             | `"http://my-rpc-address:port"`                | EL RPC provider address                                              |
| **[validator_api]**    | `auth_token`          | `"api-token-0x123456789"`                     | Authentication token for the validator keymanager API                |
| **[validator_api]**    | `ssh_address`         | `"user@server"`                               | SSH address where validator keymanager API is deployed               |
| **[validator_api]**    | `port`                | `5062`                                        | Port number for the validator keymanager API                         |


Install python dependencies

```
pip install -r requirements.txt
```


## Exceute

`python -m validator-swarm.main --n_keys <N> --index <I>`

`N` is the number of keys to be generated and submitted, and `I` is the starting index for key generation, defaults to 0.


