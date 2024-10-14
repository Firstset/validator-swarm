from .validator.exit_handler import ExitHandler

def exit(config, args):
    handler = ExitHandler(config)

    handler.exit(args.pubkey)

