import hashlib, json,time,random
from datetime import datetime
from ecdsa import SigningKey
from merkletree import MerkleTree
from transaction import Transaction
from collections import OrderedDict
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.blockchain = []
        self.transactionpool = []
        self.currentindex = 0

        #Genesis
        self.genesis_created = False
        self.genesis = self.create_first_block()

        self.peers = set()

    def register_peer(self, addr):
        #add peer to list of peers
        parsedUrl = urlparse(addr)
        if parsedUrl.netloc:
            self.peers.add(parsedUrl.netloc)
        elif parsedUrl.path:
            self.peers.add(parsedUrl.path)
        else:
            raise ValueError('Invalid URL')

    def validate_block(self,block):
        getlastblock = self.blockchain[-1][0]
        if getlastblock.hash == block.pre_hash:
            return True
        else:
            return False

    def set_blockheader(self,block):
        lastblock = self.blockchain[-1]

        # Set header values
        block.index  = len(self.blockchain) + 1
        block.pre_hash = lastblock[0].hash
        block.hash = block.hash_data()
        return block

    def add(self, block, minerpublickey):
        chain = self.blockchain
<<<<<<< HEAD
        if self.validate_block(block) == True:
            chain.append([block])
            print ("Adding Block " + str(block.index) + " to the chain at " + str(block.timestamp))
            print ("Hashed Data:", block.hash.hexdigest())
            print ("Current Number of Block is " + str(len(self.blockchain)))
=======

        chain.append([block])
        print ("Adding Block " + str(block.index) + " to the chain at " + str(block.timestamp))
        print ("Hashed Data:", block.hash.hexdigest())
        print ("Current Number of Block is " + str(len(self.blockchain)))

        self.transactionpool = []

        rewardtxn = Transaction("ServerReward", minerpublickey, 100).to_json()
        self.transactionpool.append(rewardtxn)
        print ("Rewarded Miner "+str(minerpublickey) + " with 100 SUTDcoin\n")
        return chain

    def fork(self,block1,block2,m1pk,m2pk):
        # Forcing a fork
        mainchain = self.blockchain
        currentindex = block1.index
>>>>>>> network-and-attacks

            self.transactionpool = []

<<<<<<< HEAD
            rewardtxn = Transaction("ServerReward", minerpublickey, 100).to_json()
            self.transactionpool.append(rewardtxn)
            print ("Rewarded Miner "+str(minerpublickey) + " with 100 SUTDcoin\n")
        else:
            print ("Block rejected")
        return chain
=======
        newchain2 = Blockchain()
        block2.index = currentindex
        newchain2.genesis = block2

        mainchain.append([newchain1,newchain2])
        print ("Forking occured at Block " + str(block1.index))
        self.transactionpool = []

        rewardtxn1 = Transaction("ServerReward", m1pk, 100).to_json()
        rewardtxn2 = Transaction("ServerReward", m2pk, 100).to_json()

        self.transactionpool.append(rewardtxn1)
        self.transactionpool.append(rewardtxn2)
        newchain1.transactionpool = self.transactionpool
        newchain2.transactionpool = self.transactionpool

        print ("Rewarded Miner "+str(m1pk) + " with 100 SUTDcoin\n")
        print ("Rewarded Miner "+str(m2pk) + " with 100 SUTDcoin\n")
        print (mainchain)

        return mainchain

>>>>>>> network-and-attacks

    def create_first_block(self):
        if self.genesis_created == False:
            txn1 = [Transaction('genesis_sender','ServerReward',10000).to_json()]
            self.transactionpool.append(txn1)
            self.genesis = Block(txn1)

            #genesis header - root, timestamp, prehash, nonce
            self.blockchain.append([self.genesis])
            self.genesis_created = True
            current_index = 1
            self.genesis.index = current_index
            self.currentindex = current_index
            print ("Genesis Block with index " + str(current_index) +" added at " + str(datetime.utcnow()) + " to the chain \n")

        return self.genesis

    def proof_of_work(self,block):
        while block.hash.hexdigest()[:4] != '0000':
            block.nonce += 1
            block.hash_data()

<<<<<<< HEAD
        print ("Validated proof: "+str(block.nonce))
=======
        print ("Validated proof: "+str(block.proof))
>>>>>>> network-and-attacks
        return True

    @property
    def last_block(self):
        lastblock = self.blockchain[-1]
        return lastblock

    @classmethod
    def is_valid_proof(cls, block, blockHash):
        return (blockHash.startswith('0'* self.TARGET ) and blockHash == block.hashHeader())

    @classmethod
    def is_valid_chain(cls, chain):
        prev_hash = '0'

        for block in chain:
            block_hash = block.hash

            #remove hash and recompute using compute hash method
            delattr(block, 'hash')

            if not cls.is_valid_proof(block, block.hash) or prev_hash != block.prevHash:
                return False
                break

            block.hash, prev_hash = block_hash, block_hash

        return True

    def resolve(self):
<<<<<<< HEAD
        peers = self.peers
        longest_chain = None
        currentLen = len(self.chain)

        for node in peers:
            print('http://' + node + '/chain')
            response = requests.get('http://{}/chain').format(node)

            #check if chain is longer than current one and is valid
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > currentLen and self.is_valid_chain(chain):
                    currentLen = length
                    longest_chain = chain
        #update chain to the longest one
        if longest_chain:
            self.blockchain = longest_chain
            return True

        return False

=======
        for tempblock in self.blockchain:
            #check for where the fork is
            if len(tempblock) != 1:
                print ("Forking detected",tempblock)
                for forkchain in tempblock:
                    #check which chain is longer
                    print (forkchain)
                    current_longestchain = []
                    if len(forkchain.blockchain) > len(current_longestchain):
                        current_longestchain = forkchain
                    print (current_longestchain)
                    # self.blockchain[-1] = [current_longestchain]
                    # print (self.blockchain)
                    return current_longestchain
>>>>>>> network-and-attacks

class Block:
    def __init__(self, txnlist):
        self.txnlist = txnlist
        #Header
        # Set these values from blockchain
        self.pre_hash = None
        self.index = None

        # Set when block is created
        self.nonce = 0
        self.merkle_root = self.build_tree()
        self.timestamp = time.time()

        #Hash data
        self.hash = None


    def hash_data(self):
        hashed = hashlib.sha256()
        hashed.update(str(self.pre_hash).encode('utf-8')+str(self.timestamp).encode('utf-8')+str(self.nonce).encode('utf-8')+str(self.merkle_root).encode('utf-8'))
        self.hash = hashed
        return hashed


    def build_tree(self):
        mt = MerkleTree(self.txnlist)
        buildtree= mt.build()
        merkleroot = mt.get_root()
        self.merkle_root = merkleroot

        return merkleroot

    def get_header(self):
        headerdict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "prehash": self.pre_hash,
            "merkleroot": self.merkle_root,
            "nonce": self.nonce
        }
        return headerdict
