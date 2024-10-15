from web3 import AsyncWeb3, WebSocketProvider

class NodeWSConnection():
    def __init__(self, url):
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

    def get_contract(self, address, abi):
        return self.w3.eth.contract(address=address, abi=abi)
    
