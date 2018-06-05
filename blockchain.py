'''
Block structure:
block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362
        938b9824"
}
'''
import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse


class BlockChain(object):

    def __init__(self):
        self.chain = []  # Save the block chain
        self.current_transactions = []  # save the transactions
        self.nodes = set()  # A easy way to save nodes

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    @staticmethod
    def hash(block):
        '''
        Hashes a block by SHA-256
        :param block: <dict> Block
        :return: <str> hash digest
        '''

        # We must make sure that the Dictionary is Ordered, or we'll have
        # inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        # hexdigest() method can ask the result of hash
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Return infromation of the last block
        return self.chain[-1]

    def new_block(self, proof, previous_hash=None):
        '''
        Create a new block and add it to chain.
        :param proof: <int> The proof given by Proof of Work algorithm
        :paran previous_hash: (Optional) <str> Hash of previous block
        :return: <dict> New block
        '''

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        '''
        Create a new transaction information, and add to next block.
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the block that will hold this transaction
        '''

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        '''
        A simple Proof of Work, find a number P that hash value of the string
        concatenated(hash(PP')) begin with "0000". P is the proof of currect
        block, P' is the proof of last block.
        :param last_proof: <int> The proof of last block
        :return: <int> Tha valid proof of currect block
        '''

        proof = 0
        while self.valid_proof(proof, last_proof) is False:
            proof += 1
        return proof

    def register_node(self, address):
        '''
        Add a new node to the set of nodes.
        :param address: <str> Address of node, eg.'http://192.168.1.1:5000'
        :return: None
        '''

        # urlparse class will return an instance of ParseResult class of tuple
        parsed_url = urlparse(address)
        # netloc attribute will return the network location part of address,
        # eg. '192.168.1.1:5000'
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        '''
        Determine if a given blockchain is valid, iterate each block to verify
        hash and proof of work.
        :param chain: <list> A blockchain
        :retrun: <bool> True if valid, false if not
        '''

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n============\n')

            # Check that the hash of the block is currect
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the proof of work is currect
            if not self.valid_proof(block['proof'], last_block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        '''
        Consensus Algorithm to resolve conflicts. iterate all node of
        neighbours, and use valid_chain() to verify the validity of the chain.
        If find a longer chain, replace its own chain.
        :return: <bool> True if chain be replace, flase if not
        '''

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chain from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                print('length > max_length:', length > max_length)
                print('self.valid_chain(chain):', self.valid_chain(chain))

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer then
        # ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def valid_proof(proof, last_proof):
        '''
        Verified the proof: if hash(PP') start with 0000.
        :param proof: <int> The unverified proof of currect block
        :param last_proof: <int> The proof of last block
        :return: <boolean> The proof pass verified or not
        '''

        guess = f'{proof}{last_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'
