from flask import Flask, jsonify, make_response
from uuid import uuid4
from blockchain import Blockchain
from miner import Miner
from client import SPVClient

# Instantiate Node
app =Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = Blockchain()
miner1 = Miner(blockchain)
miner2 = Miner(blockchain)

client1 = SPVClient(blockchain)
# TODO: 
# Miner: Find Block (Mining)
# Client: Made Txn, Request Txn History (blockchain and header), Get Txn + Proof

@app.route('/mine',methods=['GET'])
def mine_transaction(miner):
    # Miner send msg to network saying that the miner is mining a new block
    miner.mine()
    return "I am mining a new Block"

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    # Client make new transaction
    return "I will make a new transaction"

@app.route('/transaction/history', methods=['GET'])
def get_transaction_history():
    # Retrieve Transaction history
    # Blockchain, Header
    response = {
        'blockchain':blockchain.blockchain,
        'header':len(blockchain.blockchain)
    }
    return make_response(jsonify(response),201)

@app.route('/transaction/verify', methods=['GET'])
def verify_transaction():
    # Proof of Existence
    # Receive transaction

if __name__ == '__main__':
    app.run()