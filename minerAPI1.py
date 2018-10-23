from flask import Flask, jsonify, make_response, request
from uuid import uuid4
from blockchain import Blockchain
from miner import Miner
from client import SPVClient
import json

# Instantiate Node
app = Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = Blockchain()
m1 = Miner(blockchain)

@app.route('/peers/register', methods = ['POST'])
def register_peers():
    values = request.get_json()

    peers = values.get('peers')

    if peers is None:
        return "Error: Please provide a valid list of peers", 400

    for peer in peers:
        blockchain.register_peer(peer)

    response = {
        'message': 'New peer added.',
        'total_peers': list(blockchain.peers),
    }

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.blockchain,
        'length': len(blockchain.blockchain),
    }
    return jsonify(response), 201

@app.route('/mine',methods=['GET'])
def mine_transaction():
    new_block, txns = m1.mine(blockchain)
    blockHeader = new_block.get_header()
    # Miner send msg to network saying that the miner is mining a new block
    response = {
            'message': "New Block Forged",
            'block_index': blockHeader['index'],
            'transactions': txns,
            'nonce': block['nonce'],
            'previous_hash': blockHeader['prehash'],
        }
    return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    # Client make new transaction
    values = request.form
    required = ['receiver', 'amount']

    # if not all(k in values for k in required):
    #     return 'Missing values', 400

    txn = m1.new_txn(values['receiver'], values['amount'])

    response = {'message':'Transaction successfully created'}

    return jsonify(response), 201

# @app.route('/transaction/history', methods=['GET'])
# def get_transaction_history():
#     # Retrieve Transaction history
#     # Blockchain, Header
#     response = {
#         'blockchain':blockchain.blockchain,
#         'header':len(blockchain.blockchain)
#     }
#     return make_response(jsonify(response),201)

@app.route('/peers/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.blockchain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.blockchain
        }
    return jsonify(response), 200

@app.route('/transaction/verify', methods=['GET'])
def verify_transaction():
    
    pass
    # Proof of Existence
    # Receive transaction

if __name__ == '__main__':
    # from argparse import ArgumentParser
    #
    # parser = ArgumentParser()
    # parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    # args = parser.parse_args()
    # port = args.port

    app.run(host="localhost", port=5000, debug=True)
