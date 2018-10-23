from flask import Flask, jsonify, make_response, request
from uuid import uuid4
from blockchain import Blockchain
from client import SPVClient
import json

# Instantiate Node
app = Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = Blockchain()
client1 = SPVClient()

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

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    # Client make new transaction
    values = request.get_json()

    required = ['receiver', 'amount']

    if not all(k in values for k in required):
        return 'Missing values', 400

    txn = client1.new_txn(values['receiver'], values['amount'])

    response = {'message':'Transaction successfully created'}

    return jsonify(response), 201

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5003, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host="localhost", port=port, debug=True)
