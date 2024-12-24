import random

class ZKPTransaction:
    def __init__(self, user_id, donation_amount, charity, p, g):
        self.user_id = user_id
        self.donation_amount = donation_amount
        self.charity = charity
        self.p = p
        self.g = g
        self.x = None  # Secret (hashed password or equivalent)
        self.y = None  # Public key
        self.r = None  # Random commitment
        self.h = None  # Commitment
        self.b = None  # Challenge bit
        self.s = None  # Response

    def create_proof(self):
        """
        Step 1: Prover (user) generates the public key and commitment.
        """
        self.x = random.randint(1, self.p - 2)  # Normally derived from the password
        self.y = pow(self.g, self.x, self.p)
        self.r = random.randint(0, self.p - 2)
        self.h = pow(self.g, self.r, self.p)

    def receive_challenge(self):
        """
        Step 2: Verifier sends a random challenge bit.
        """
        self.b = random.randint(0, 1)

    def send_response(self):
        """
        Step 3: Prover calculates and sends the response.
        """
        self.s = (self.r + self.b * self.x) % (self.p - 1)

    def verify_proof(self):
        """
        Step 4: Verifier checks the proof.
        """
        left = pow(self.g, self.s, self.p)
        right = (self.h * pow(self.y, self.b, self.p)) % self.p
        return left == right
