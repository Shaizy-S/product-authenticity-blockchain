import hashlib
import json
from time import time
from typing import Any, Dict, List, Optional
import secrets


class MerkleTree:
    """Merkle Tree implementation for transaction verification"""
    
    @staticmethod
    def hash_data(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def build_merkle_root(transactions: List[Dict]) -> str:
        """Build Merkle root from list of transactions"""
        if not transactions:
            return MerkleTree.hash_data("empty")
        
        # Hash all transactions
        hashes = [MerkleTree.hash_data(json.dumps(tx, sort_keys=True)) 
                  for tx in transactions]
        
        # Build tree bottom-up
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])  # Duplicate last hash if odd
            
            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_level.append(MerkleTree.hash_data(combined))
            hashes = new_level
        
        return hashes[0]


class DigitalSignature:
    """Simplified digital signature system"""
    
    @staticmethod
    def generate_keypair() -> tuple:
        """Generate a simple keypair (private_key, public_key)"""
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return private_key, public_key
    
    @staticmethod
    def sign_data(data: str, private_key: str) -> str:
        """Sign data with private key"""
        combined = data + private_key
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_signature(data: str, signature: str, public_key: str) -> bool:
        """Verify signature (simplified version)"""
        # In real blockchain, this would use asymmetric cryptography
        return len(signature) == 64 and len(public_key) == 64


class Transaction:
    """Represents a product registration transaction"""
    
    def __init__(self, product_data: Dict[str, Any], manufacturer_signature: str = None):
        self.timestamp = time()
        self.product_data = product_data
        self.manufacturer_signature = manufacturer_signature
        self.transaction_id = self._generate_transaction_id()
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        tx_string = json.dumps({
            'timestamp': self.timestamp,
            'product_data': self.product_data
        }, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp,
            'product_data': self.product_data,
            'manufacturer_signature': self.manufacturer_signature
        }


class Block:
    """Represents a block in the blockchain containing transactions"""
    
    def __init__(self, index: int, transactions: List[Transaction], 
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = MerkleTree.build_merkle_root(
            [tx.to_dict() for tx in transactions]
        )
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root,
            'hash': self.hash
        }


class Blockchain:
    """Main blockchain class with enhanced features"""
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty  # Mining difficulty
        self.mining_reward = 1.0
        self.manufacturers: Dict[str, Dict] = {}  # Store manufacturer keys
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_transaction = Transaction({
            'product_name': 'Genesis Block',
            'manufacturer': 'System',
            'batch_number': 'GENESIS-001',
            'manufacture_date': '2025-01-01',
            'product_id': 'genesis'
        })
        
        genesis_block = Block(0, [genesis_transaction], "0")
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def register_manufacturer(self, manufacturer_name: str) -> Dict[str, str]:
        """Register a manufacturer and generate keypair"""
        if manufacturer_name in self.manufacturers:
            return self.manufacturers[manufacturer_name]
        
        private_key, public_key = DigitalSignature.generate_keypair()
        
        self.manufacturers[manufacturer_name] = {
            'name': manufacturer_name,
            'public_key': public_key,
            'private_key': private_key,
            'registered_at': time()
        }
        
        return self.manufacturers[manufacturer_name]
    
    def create_transaction(self, product_name: str, manufacturer: str,
                          batch_number: str, manufacture_date: str,
                          private_key: str = None) -> str:
        """Create a new product registration transaction"""
        
        # Register manufacturer if not exists
        if manufacturer not in self.manufacturers:
            self.register_manufacturer(manufacturer)
        
        # Generate unique product ID
        product_data = {
            'product_name': product_name,
            'manufacturer': manufacturer,
            'batch_number': batch_number,
            'manufacture_date': manufacture_date,
            'registration_time': time()
        }
        
        product_id = hashlib.sha256(
            json.dumps(product_data, sort_keys=True).encode()
        ).hexdigest()
        
        product_data['product_id'] = product_id
        
        # Sign transaction
        if private_key:
            signature = DigitalSignature.sign_data(
                json.dumps(product_data, sort_keys=True),
                private_key
            )
        else:
            signature = "unsigned"
        
        # Create transaction
        transaction = Transaction(product_data, signature)
        self.pending_transactions.append(transaction)
        
        return product_id
    
    def mine_pending_transactions(self, miner_address: str = "system") -> Block:
        """Mine pending transactions into a new block"""
        
        if not self.pending_transactions:
            return None
        
        # Create new block with pending transactions
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=previous_block.hash
        )
        
        # Proof of Work - mine the block
        print(f"Mining block {new_block.index}...")
        new_block = self._proof_of_work(new_block)
        print(f"Block mined! Hash: {new_block.hash[:16]}...")
        
        # Add block to chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block
    
    def _proof_of_work(self, block: Block) -> Block:
        """Perform proof of work mining"""
        target = '0' * self.difficulty
        
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        
        return block
    
    def get_latest_block(self) -> Block:
        """Get the last block in the chain"""
        return self.chain[-1]
    
    def is_chain_valid(self) -> tuple:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False, f"Block {i} has been tampered with (hash mismatch)"
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False, f"Block {i} has invalid previous hash link"
            
            # Check proof of work
            if not current_block.hash.startswith('0' * self.difficulty):
                return False, f"Block {i} has invalid proof of work"
            
            # Verify Merkle root
            expected_merkle = MerkleTree.build_merkle_root(
                [tx.to_dict() for tx in current_block.transactions]
            )
            if current_block.merkle_root != expected_merkle:
                return False, f"Block {i} has invalid Merkle root"
        
        return True, "Blockchain is valid"
    
    def verify_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Verify if a product exists in any block"""
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.product_data.get('product_id') == product_id:
                    product_data = transaction.product_data.copy()
                    product_data['block_index'] = block.index
                    product_data['block_hash'] = block.hash
                    product_data['transaction_id'] = transaction.transaction_id
                    product_data['is_authentic'] = True
                    product_data['confirmed_blocks'] = len(self.chain) - block.index
                    return product_data
        
        return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from all blocks"""
        products = []
        
        for block in self.chain:
            if block.index == 0:  # Skip genesis block
                continue
            
            for transaction in block.transactions:
                product_info = transaction.product_data.copy()
                product_info['block_index'] = block.index
                product_info['transaction_id'] = transaction.transaction_id
                products.append(product_info)
        
        return products
    
    def get_block_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get detailed block information"""
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_products': total_transactions - 1,  # Exclude genesis
            'difficulty': self.difficulty,
            'registered_manufacturers': len(self.manufacturers),
            'pending_transactions': len(self.pending_transactions),
            'chain_valid': self.is_chain_valid()[0]
        }
        
    def save_to_file(self, filename: str = 'blockchain_data.json'):
        """Save blockchain to file"""
        import json
        data = {
            'chain': [block.to_dict() for block in self.chain],
            'manufacturers': self.manufacturers,
            'difficulty': self.difficulty
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Blockchain saved to {filename}")
    
    def load_from_file(self, filename: str = 'blockchain_data.json') -> bool:
        """Load blockchain from file"""
        import json
        import os
        
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Reconstruct blockchain
            self.chain = []
            self.manufacturers = data.get('manufacturers', {})
            self.difficulty = data.get('difficulty', 4)
            
            for block_data in data['chain']:
                transactions = []
                for tx_data in block_data['transactions']:
                    tx = Transaction(tx_data['product_data'], tx_data.get('manufacturer_signature'))
                    tx.transaction_id = tx_data['transaction_id']
                    tx.timestamp = tx_data['timestamp']
                    transactions.append(tx)
                
                block = Block(
                    block_data['index'],
                    transactions,
                    block_data['previous_hash'],
                    block_data['nonce']
                )
                block.merkle_root = block_data['merkle_root']
                block.hash = block_data['hash']
                block.timestamp = block_data['timestamp']
                self.chain.append(block)
            
            print(f"✓ Blockchain loaded from {filename}")
            return True
        except Exception as e:
            print(f"✗ Error loading blockchain: {e}")
            return False