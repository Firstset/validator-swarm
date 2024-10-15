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
