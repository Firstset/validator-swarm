import aiohttp
import asyncio
from .util import load_json_file
import os
from .connection.connection import NodeWSConnection
from .protocol.csm import CSM
from .exception import RelayRequestException


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
        async with session.get(url, params={'pubkey': pubkey}, timeout=5) as response:
            if response.status == 200:
                return True
            return False
    except Exception as e:
        print(f"Warning: Could not check registration status for {relay_url}: {str(e)}")
        return None  # Return None to indicate unknown status

async def get_validator_keys_from_csm(config):
    csm = CSM(config)
    id = config['csm']['node_operator_id']
    return await csm.get_registered_keys(id)

async def check_relays(config, args):
    """Main function to check relay coverage for validators"""
    print("Checking relay coverage for validators...")

    # Get whitelisted relays
    relay_tuples = await get_whitelisted_relays(config)
    relay_urls = [relay[0] for relay in relay_tuples]
    
    # Separate mandatory and optional relays
    mandatory_relays = [relay[0] for relay in relay_tuples if relay[2]]  # relay[2] is the mandatory flag
    optional_relays = [relay[0] for relay in relay_tuples if not relay[2]]
    
    print(f"Found {len(relay_urls)} whitelisted relays ({len(mandatory_relays)} mandatory, {len(optional_relays)} optional)")
    
    # Get validator public keys from CSM
    validator_keys = await get_validator_keys_from_csm(config)
    print(f"Found {len(validator_keys)} validators in CSM")
    
    # Check registration for each validator with each relay
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # Process validators in chunks to limit concurrency
        chunk_size = 10
        for i in range(0, len(validator_keys), chunk_size):
            validator_chunk = validator_keys[i:i + chunk_size]
            
            tasks = []
            for validator in validator_chunk:
                results[validator] = {
                    'mandatory_total': 0,
                    'optional_total': 0,
                    'mandatory_relays': [],
                    'optional_relays': [],
                    'unknown': []
                }
                for relay_url in relay_urls:
                    tasks.append(check_validator_registration(session, relay_url, validator))
            
            chunk_results = await asyncio.gather(*tasks)
            
            for validator_idx, validator in enumerate(validator_chunk):
                for relay_idx, is_registered in enumerate(chunk_results[validator_idx * len(relay_urls):(validator_idx + 1) * len(relay_urls)]):
                    relay_url = relay_urls[relay_idx]
                    if is_registered is True:
                        if relay_url in mandatory_relays:
                            results[validator]['mandatory_total'] += 1
                            results[validator]['mandatory_relays'].append(relay_url)
                        else:
                            results[validator]['optional_total'] += 1
                            results[validator]['optional_relays'].append(relay_url)
                    elif is_registered is None:
                        results[validator]['unknown'].append(relay_url)
            
            print(f"Processed {min(i + chunk_size, len(validator_keys))}/{len(validator_keys)} validators...")
        
        # Print results based on mode
        if hasattr(args, 'detailed') and args.detailed:
            print_detailed_report(results, relay_tuples, mandatory_relays, optional_relays)
        else:
            print_summary_report(results, mandatory_relays, optional_relays)

def print_summary_report(results, mandatory_relays, optional_relays):
    """Print condensed summary of validator relay registration status"""
    print("\nRelay Coverage Summary:")
    print("-" * 50)
    
    ok_count = 0
    not_ok_count = 0
    
    for validator, data in results.items():
        is_ok = data['mandatory_total'] >= 2  # At least 2 mandatory relays required
        status = "OK" if is_ok else "NOT OK"
        
        if is_ok:
            ok_count += 1
        else:
            not_ok_count += 1
            
        mandatory_coverage = f"{data['mandatory_total']}/{len(mandatory_relays)}"
        optional_coverage = f"{data['optional_total']}/{len(optional_relays)}"
        
        print(f"Validator {validator[:12]}... : {status:6} (Mandatory: {mandatory_coverage}, Optional: {optional_coverage})")
    
    print(f"\nSummary: {ok_count} validators OK, {not_ok_count} validators NOT OK")

def print_detailed_report(results, relay_tuples, mandatory_relays, optional_relays):
    """Print detailed report of validator relay registration status"""
    print("\nDetailed Relay Coverage Report:")
    print("-" * 50)
    
    for validator, data in results.items():
        is_ok = data['mandatory_total'] >= 2
        status = "OK" if is_ok else "NOT OK"
        
        print(f"\nValidator {validator[:12]}... : {status}")
        print(f"Registered with {data['mandatory_total']}/{len(mandatory_relays)} mandatory relays")
        print(f"Registered with {data['optional_total']}/{len(optional_relays)} optional relays")
        
        if data['unknown']:
            print(f"Could not check status for {len(data['unknown'])} relay(s):")
            for relay in data['unknown']:
                relay_info = next(r for r in relay_tuples if r[0] == relay)
                print(f"  ? {relay} ({relay_info[1]} - {relay_info[3]})")
        
        missing_mandatory = set(mandatory_relays) - set(data['mandatory_relays'])
        if missing_mandatory:
            print("Missing mandatory registrations:")
            for relay in missing_mandatory:
                relay_info = next(r for r in relay_tuples if r[0] == relay)
                print(f"  - {relay} ({relay_info[1]} - {relay_info[3]})")
        
        missing_optional = set(optional_relays) - set(data['optional_relays'])
        if missing_optional:
            print("Missing optional registrations:")
            for relay in missing_optional:
                relay_info = next(r for r in relay_tuples if r[0] == relay)
                print(f"  - {relay} ({relay_info[1]} - {relay_info[3]})")
