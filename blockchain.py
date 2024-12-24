import hashlib
import time

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = (
            str(self.index)
            + str(self.transactions)
            + self.previous_hash
            + str(self.timestamp)
            + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, user_id, donation_amount, charity, p, g):
        transaction = {
            "sender": user_id,
            "amount": donation_amount,
            "recipient": charity,
            "p": p,
            "g": g
        }
        self.pending_transactions.append(transaction)




    def mine_block(self, miner_address):
        if not self.pending_transactions:
            return None

        last_block = self.get_last_block()
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=last_block.hash,
        )

        # Proof-of-Work: increment nonce by a random value until a hash with leading zeros is found
        difficulty = 4
        while not new_block.hash.startswith("0" * difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        self.chain.append(new_block)
        self.pending_transactions = []

        # Reward the miner
        self.add_transaction({
            "sender": "network",
            "recipient": miner_address,
            "amount": 1
        })

        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Validate hash
            if current.hash != current.compute_hash():
                return False

            # Validate previous hash
            if current.previous_hash != previous.hash:
                return False

        return True

    def view_user(self, user_id):
        user_transactions = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get("sender") == user_id or transaction.get("recipient") == user_id:
                    user_transactions.append(transaction)
        return user_transactions
