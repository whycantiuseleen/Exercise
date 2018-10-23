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
