class ConfigException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InputException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class DepositException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class KeyExistsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ValidatorLoadException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ValidatorReadException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ValidatorDeleteException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CSMSubmissionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ExitSignException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ExitBroadcastException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TransactionRejectedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RemoteSignerURLException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ExecutionLayerRPCException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConsensusLayerRPCException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SSHTunnelException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RelayRequestException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
