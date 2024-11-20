import aiohttp
import asyncio
from .util import load_json_file
import os
from .connection.connection import NodeWSConnection
from .protocol.csm import CSM
async def get_whitelisted_relays(config):
    """Fetch whitelisted relays from the allowlist contract"""
    async with NodeWSConnection(config['rpc']['execution_address']) as con:
        contract = con.get_contract(
            address=config['relay_allowlist_address'],
            abi=load_json_file(os.path.join(os.getcwd(), 'abis', 'relay_allowlist.json'))
        )
        relays = await contract.functions.get_relays().call()
        return relays

async def check_validator_registration(session, relay_url, pubkey):
    """Check if a validator is registered with a specific relay"""
    url = f"{relay_url}/relay/v1/data/validator_registration"
    try:
        async with session.get(url, params={'pubkey': pubkey}) as response:
            if response.status == 200:
                return True
            return False
    except:
        return False

async def get_validator_keys_from_csm(config):
    csm = CSM(config)
    id = config['csm']['node_operator_id']
    return await csm.get_registered_keys(id)

async def check_relays(config, args):
    """Main function to check relay coverage for validators"""
    print("Checking relay coverage for validators...")

    # Get whitelisted relays
    relay_tuples = await get_whitelisted_relays(config)
    # Extract just the URLs from the relay tuples
    relay_urls = [relay[0] for relay in relay_tuples]
    print(f"Found {len(relay_urls)} whitelisted relays")
    
    # Get validator public keys from CSM
    validator_keys = await get_validator_keys_from_csm(config)
    print(f"Found {len(validator_keys)} validators in CSM")
    
    # Check registration for each validator with each relay
    async with aiohttp.ClientSession() as session:
        results = {}
        for validator in validator_keys:
            results[validator] = {'total': 0, 'relays': []}
            
            for relay_url in relay_urls:
                is_registered = await check_validator_registration(session, relay_url, validator)
                if is_registered:
                    results[validator]['total'] += 1
                    results[validator]['relays'].append(relay_url)
        
        # Print results
        print("\nRelay coverage report:")
        print("-" * 50)
        for validator, data in results.items():
            coverage_pct = (data['total'] / len(relay_urls)) * 100
            print(f"\nValidator {validator[:12]}...")
            print(f"Registered with {data['total']}/{len(relay_urls)} relays ({coverage_pct:.1f}%)")
            if data['total'] < len(relay_urls):
                print("Missing registrations for relays:")
                missing_relays = set(relay_urls) - set(data['relays'])
                for relay in missing_relays:
                    # Find the full relay info for prettier printing
                    relay_info = next(r for r in relay_tuples if r[0] == relay)
                    print(f"  - {relay} ({relay_info[1]} - {relay_info[3]})")
