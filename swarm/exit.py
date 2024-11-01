import web3
from argparse import Namespace
from .validator.exit_handler import ExitHandler
from .protocol.csm import CSM


async def exit(config: dict, args: Namespace) -> None:
    handler = ExitHandler(config)

    handler.exit(args.pubkey)


async def automated_exit(config: dict, args: Namespace) -> None:

    csm = CSM(config)
    handler = ExitHandler(config)

    if args.telegram:
        await handler.send_telegram_message('Automated exit monitor started')
    
    async for exit_event in csm.exit_monitor():
        pubkey = web3.Web3.to_hex(exit_event.args.validatorPubkey)
        print(f'Requested exit for validator with pubkey {pubkey}')
        if args.delete:
            handler.exit(pubkey)
        if args.telegram:
            await handler.send_telegram_message(f'Requested exit for validator with pubkey {pubkey}')