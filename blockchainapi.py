from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import BlockChain

# Instantiate the node
app = Flask(__name__)

# Generate a globally uniqe address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Provide rewards for the node which proof the work. Sender 0 means that
    # coin is new dig out.
    blockchain.new_transaction(sender=0, recipient=node_identifier, amount=1)

    # Forge the new block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': 'New block forge',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    '''
    Add a new transaction
    Transaction structure
    {
        "sender": "my address",
        "recipient": "someone else's address",
        "amount": 5
    }
    '''
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_transaction(
        values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be add to Block{index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    # Return information of all block on the chain
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    # return a response in json format and Content-Type is application/json).
    # If use json.dump will return a response in json fromat, but Content-Type
    # is text/html.
    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    # Resolve the conflicts
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    # Register the nodes
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return 'Error: Please supply a valid set of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New node have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1')
