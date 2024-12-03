import argparse
import toml
import sys 
import asyncio
from . import state_check, deploy, exit, local_sign, relay_check
from .util import load_chain_addresses

if __name__ == '__main__':
 
    try:
        config = toml.load("./config.toml")
        config = load_chain_addresses(config)
    except Exception as e:
        sys.exit(f'Error: unable to load configuration. {e}')

    parser = argparse.ArgumentParser(description="validator-swarm :)")
    
    # Create a subparsers object to hold the subcommands
    subparsers = parser.add_subparsers(help="Available commands")

    parser_state_check = subparsers.add_parser('state-check', help='compare the uploaded keys to protocol against loaded keystores in validator')
    parser_state_check.add_argument('--delete', action='store_true', help="delete dangling validators")
    parser_state_check.set_defaults(func=state_check.do_check)

    parser_deploy = subparsers.add_parser('deploy', help='Validator key creation and deployment into CSM and validator client')
    parser_deploy.add_argument('-n', '--n_keys', type=int, required=True, help='the number of keys to be created')
    parser_deploy.add_argument('-i', '--index', type=int, default=0, help='the starting key index')
    parser_deploy.add_argument('-r', '--remote_sign', action='store_true', help='if true, validators will be configured with remote signing')
    parser_deploy.set_defaults(func=deploy.deploy)
    
    parser_exit = subparsers.add_parser('exit', help='Exit a validator')
    parser_exit.add_argument('--pubkey', type=str, help='the public key of the validator to be exited')
    parser_exit.set_defaults(func=exit.exit)
    
    parser_exit_monitor = subparsers.add_parser('auto_exit', help='Monitor for validator exit requests')
    parser_exit_monitor.add_argument('--delete', action='store_true', help='automatically exit validators')
    parser_exit_monitor.add_argument('--telegram', action='store_true', help='send telegram notifications')
    parser_exit_monitor.set_defaults(func=exit.automated_exit)
    
    parser_relay_check = subparsers.add_parser('relay-check', help='Check validator relay coverage against allowed mev-boost relays')
    parser_relay_check.add_argument('--detailed', action='store_true', help='Show detailed registration information')
    parser_relay_check.set_defaults(func=relay_check.check_relays)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        t = asyncio.run(args.func(config, args))
    else:
        parser.print_help()
