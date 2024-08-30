# Lido CSM one-shot validator spawning

## Requirements

- The (deposit key generation tool)[]

- A previously generated seed phrase

- An execution layer RPC address
- A synchronized, running Ethereum node  (EL + CL)
    - An Ethereum account managed by the node, able to sign transactions.
- A running validator client with support for mutiple key management (e.g. Lighthouse)
    - With active Keymanager API listening in localhost
    - Reachable through ssh

## Setup

Copy `config.toml.example` to `config.toml` and fill with your configuration values

Install python dependencies

```
pip install -r requirements.txt
```


## Exceute

`python -m bulk-deploy.main --n_keys <N> --index <I>`

`N` is the number of keys to be generated and submitted, and `I` is the starting index for key generation.


