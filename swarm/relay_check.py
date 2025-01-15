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

async def check_validator_registration(session, relay_url, pubkey, config):
    """Check if a validator is registered with a specific relay and verify fee recipient"""
    url = f"{relay_url}/relay/v1/data/validator_registration"
    
    try:
        async with session.get(url, params={'pubkey': pubkey}, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                if 'message' in data and 'fee_recipient' in data['message']:
                    fee_recipient = data['message']['fee_recipient']
                    # Return tuple of (registration status, fee recipient)
                    return (True, fee_recipient.lower() == config['fee_recipient'].lower(), fee_recipient)
                return (False, False, None)
            return (False, False, None)
    except Exception as e:
        print(f"Warning: Could not check registration status for {relay_url}: {str(e)}")
        return None

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
    
    # If pubkey is specified, only check that validator
    if hasattr(args, 'pubkey') and args.pubkey:
        if args.pubkey not in validator_keys:
            print(f"Error: Validator {args.pubkey} not found in CSM")
            return
        validator_keys = [args.pubkey]
        print(f"Checking specific validator: {args.pubkey}")
    else:
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
                    'unknown': [],
                    'fee_mismatches': []  # Add this field to track fee mismatches
                }
                for relay_url in relay_urls:
                    tasks.append(check_validator_registration(session, relay_url, validator, config))
            
            chunk_results = await asyncio.gather(*tasks)
            
            for validator_idx, validator in enumerate(validator_chunk):
                for relay_idx, result in enumerate(chunk_results[validator_idx * len(relay_urls):(validator_idx + 1) * len(relay_urls)]):
                    relay_url = relay_urls[relay_idx]
                    if result is None:
                        results[validator]['unknown'].append(relay_url)
                    else:
                        is_registered, fee_matches, fee_recipient = result
                        if is_registered:
                            if not fee_matches:
                                results[validator]['fee_mismatches'].append((relay_url, fee_recipient))
                            
                            if relay_url in mandatory_relays:
                                results[validator]['mandatory_total'] += 1
                                results[validator]['mandatory_relays'].append(relay_url)
                            else:
                                results[validator]['optional_total'] += 1
                                results[validator]['optional_relays'].append(relay_url)
            
            if not args.pubkey:  # Only show progress for bulk checks
                print(f"Processed {min(i + chunk_size, len(validator_keys))}/{len(validator_keys)} validators...")
        
        # Print results based on mode
        if args.pubkey or (hasattr(args, 'detailed') and args.detailed):
            print_detailed_report(results, relay_tuples, mandatory_relays, optional_relays)
        else:
            print_summary_report(results, mandatory_relays, optional_relays)

def print_summary_report(results, mandatory_relays, optional_relays):
    """Print condensed summary of validator relay registration status"""
    print("\nRelay Coverage Summary:")
    print("-" * 50)
    
    ok_count = 0
    not_ok_count = 0
    fee_mismatch_count = 0
    
    for validator, data in results.items():
        has_fee_mismatch = len(data.get('fee_mismatches', [])) > 0
        is_ok = data['mandatory_total'] >= 2 and not has_fee_mismatch  # At least 2 mandatory relays required and no fee mismatches
        
        status = "OK" if is_ok else "NOT OK"
        if has_fee_mismatch:
            status += " (⚠️ Fee mismatch)"
            fee_mismatch_count += 1
        
        if is_ok and not has_fee_mismatch:
            ok_count += 1
        else:
            not_ok_count += 1
            
        mandatory_coverage = f"{data['mandatory_total']}/{len(mandatory_relays)}"
        optional_coverage = f"{data['optional_total']}/{len(optional_relays)}"
        
        print(f"Validator {validator} : {status:6} (Mandatory: {mandatory_coverage}, Optional: {optional_coverage})")
    
    print(f"\nSummary: {ok_count} validators OK, {not_ok_count} validators NOT OK")
    if fee_mismatch_count > 0:
        print(f"Warning: {fee_mismatch_count} validators have fee recipient mismatches")
    else:
        print("All validators have correct fee recipient set")

def print_detailed_report(results, relay_tuples, mandatory_relays, optional_relays):
    """Print detailed report of validator relay registration status"""
    print("\nDetailed Relay Coverage Report:")
    print("-" * 50)
    
    for validator, data in results.items():
        has_fee_mismatch = len(data.get('fee_mismatches', [])) > 0
        is_ok = data['mandatory_total'] >= 2 and not has_fee_mismatch
        
        status = "OK" if is_ok else "NOT OK"
        if has_fee_mismatch:
            status += " (⚠️ Fee mismatch)"
        
        print(f"\nValidator {validator} : {status}")
        print(f"Registered with {data['mandatory_total']}/{len(mandatory_relays)} mandatory relays")
        print(f"Registered with {data['optional_total']}/{len(optional_relays)} optional relays")
        
        if data.get('fee_mismatches'):
            print("\nFee recipient mismatches:")
            for relay, incorrect_fee in data['fee_mismatches']:
                relay_info = next(r for r in relay_tuples if r[0] == relay)
                print(f"  ! {relay} ({relay_info[1]} - {relay_info[3]}) - Incorrect fee recipient: {incorrect_fee}")
        else:
            print("Fee recipient is correctly set for all relays")
        
