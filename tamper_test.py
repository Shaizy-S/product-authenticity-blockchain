# tamper_test.py
import json
import copy
import hashlib
from pathlib import Path
from itertools import zip_longest

CHAIN_FILE = "blockchain_data.json"  # change if your file has a different name
DIFFICULTY_PREFIX = None  # will be read from file

def sha256_hex(s: bytes) -> str:
    return hashlib.sha256(s).hexdigest()

def compute_block_hash(block: dict) -> str:
    """
    Compute the block hash the same way your blockchain likely does:
    - Make a shallow copy and remove the 'hash' field if present
    - JSON dump with sort_keys=True, encode and sha256
    """
    block_copy = dict(block)
    block_copy.pop("hash", None)
    # Ensure deterministic serialization: sort keys
    encoded = json.dumps(block_copy, sort_keys=True).encode()
    return sha256_hex(encoded)

def merkle_root_from_transactions(tx_list: list) -> str:
    """
    Compute merkle root from list of transactions (transaction JSON).
    Uses sha256 over JSON string of transaction (sorted keys).
    If odd number, duplicate last hash (standard simple approach).
    """
    if not tx_list:
        return sha256_hex(b"")
    # leaf hashes
    leaves = [sha256_hex(json.dumps(tx, sort_keys=True).encode()) for tx in tx_list]
    # build up the tree
    level = leaves
    while len(level) > 1:
        next_level = []
        for a, b in zip_longest(level[0::2], level[1::2], fillvalue=level[-1]):
            combined = (a + b).encode()
            next_level.append(sha256_hex(combined))
        level = next_level
    return level[0]

def validate_chain(chain_data: dict, verbose=True):
    """
    Validate chain structure:
      - previous_hash links
      - recompute block.hash matches stored hash
      - recompute merkle root matches stored merkle_root
      - proof-of-work: block.hash startswith required zeros (difficulty)
    Returns (is_valid, list_of_errors)
    """
    errors = []
    chain = chain_data.get("chain", [])
    difficulty = chain_data.get("difficulty")
    prefix = "0" * difficulty if isinstance(difficulty, int) else None

    for i, block in enumerate(chain):
        idx = block.get("index", i)
        # 1) Check previous_hash
        if i == 0:
            expected_prev = "0"
        else:
            expected_prev = chain[i-1].get("hash")
        if block.get("previous_hash") != expected_prev:
            errors.append(f"Block index {idx}: previous_hash mismatch. expected {expected_prev}, found {block.get('previous_hash')}")
        # 2) Recompute merkle root
        txs = block.get("transactions", [])
        recomputed_merkle = merkle_root_from_transactions(txs)
        stored_merkle = block.get("merkle_root")
        if stored_merkle != recomputed_merkle:
            errors.append(f"Block index {idx}: merkle_root mismatch.\n  stored: {stored_merkle}\n  recomputed: {recomputed_merkle}")
        # 3) Recompute block hash (based on all block fields except 'hash')
        recomputed_hash = compute_block_hash(block)
        stored_hash = block.get("hash")
        if recomputed_hash != stored_hash:
            errors.append(f"Block index {idx}: block hash mismatch.\n  stored: {stored_hash}\n  recomputed: {recomputed_hash}")
        # 4) Proof-of-Work: stored_hash must start with prefix (if difficulty present)
        if prefix is not None:
            if not (isinstance(stored_hash, str) and stored_hash.startswith(prefix)):
                errors.append(f"Block index {idx}: proof-of-work failed (hash does not start with '{prefix}'). hash={stored_hash}")

    is_valid = len(errors) == 0
    if verbose:
        if is_valid:
            print("✅ Blockchain VALID — all checks passed.")
        else:
            print("❌ Blockchain INVALID — found problems:")
            for e in errors:
                print(" -", e)
    return is_valid, errors

def load_chain(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{path} not found")
    return json.loads(p.read_text())

def save_chain(path: str, data: dict):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=False))

def main():
    print("Loading chain file:", CHAIN_FILE)
    chain_data = load_chain(CHAIN_FILE)
    print("Running validation on original blockchain...")
    validate_chain(chain_data)

    # Make a tampered copy for demonstration
    tampered = copy.deepcopy(chain_data)

    # Choose a block and transaction to tamper with (safe defaults)
    # We'll attempt to change block index 1 transaction product_name
    try:
        target_block_index = 1
        block = tampered["chain"][target_block_index]
        tx = block["transactions"][0]
        orig_name = tx["product_data"].get("product_name")
        print(f"\nOriginal product_name in block {target_block_index} tx0: {orig_name!r}")
        # Tamper: change product name
        tx["product_data"]["product_name"] = (orig_name or "") + " [TAMPERED]"
        print(f"Tampered product_name to: {tx['product_data']['product_name']!r}")
    except Exception as e:
        print("Could not tamper block as planned:", e)
        return

    # Save tampered to a temporary file so you can inspect if desired
    tampered_file = "blockchain_tampered.json"
    save_chain(tampered_file, tampered)
    print(f"\nSaved tampered copy to {tampered_file}")

    print("\nRunning validation on tampered blockchain...")
    validate_chain(tampered)

    print("\nDemo complete. You should see errors reported above for the tampered chain.")
    print("If you saw NO errors for the tampered chain, tell me the exact output and your blockchain class' `is_chain_valid()` implementation and I will adapt the check to match your code.")

if __name__ == "__main__":
    main()
