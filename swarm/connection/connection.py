from eth_typing import Address
from web3 import AsyncWeb3, WebSocketProvider
from web3.contract import AsyncContract

class NodeWSConnection():
    def __init__(self, url: str) -> None:
        self.url = url

    async def __aenter__(self):
        self.w3 = AsyncWeb3(WebSocketProvider(self.url))
        await self.w3.provider.connect()
        return self

    async def __aexit__(self, exception_type, exception_value, _):
        if exception_type:
            print(f'Exception: {exception_type} {exception_value}')

        await self.w3.provider.disconnect()
        return False

    def get_contract(self, address: Address, abi: dict) -> AsyncContract:
            # os.remove(directory) ?
        return self.w3.eth.contract(address=address, abi=abi)
    
