import hashlib, json
import time
from datetime import datetime
from ecdsa import SigningKey
from merkletree import MerkleTree
from transaction import Transaction
import random

class Blockchain:
    def __init__(self):
        self.blockchain = []   
        self.transactionpool = []
      
        #Genesis
        self.genesis_created = False
        self.genesis = self.create_first_block()

    def validate_block(self,block):
        getlastblock = self.blockchain[-1]
        if getlastblock.hash == block.pre_hash:
            return True
        else:
            return False
        
    def set_blockheader(self,block):
        lastblock = self.blockchain[-1] 
    
        # Set header values
        block.index = len(self.blockchain) + 1
        block.pre_hash = lastblock[0].hash
        block.hash = block.hash_data()
        return block

    def add(self, block, minerpublickey):
        chain = self.blockchain
    
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
        chain = self.blockchain
        block1.index = block2.index
        chain.append([block1,block2])
        print ("Forking occured at Block " + str(block1.index))
        self.transactionpool = []
        
        rewardtxn1 = Transaction("ServerReward", m1pk, 100).to_json()
        rewardtxn2 = Transaction("ServerReward", m2pk, 100).to_json()
        
        self.transactionpool.append(rewardtxn1)
        self.transactionpool.append(rewardtxn2)
        print ("Rewarded Miner "+str(m1pk) + " with 100 SUTDcoin\n")
        print ("Rewarded Miner "+str(m2pk) + " with 100 SUTDcoin\n")
        print (chain)
        
        return chain
        

    def create_first_block(self):
        if self.genesis_created == False:
            txn1 = [Transaction('genesis_sender','ServerReward',10000).to_json()]
            self.transactionpool.append(txn1)
            self.genesis = Block(txn1)
            
            #genesis header - root, timestamp, prehash, nonce
            self.blockchain.append([self.genesis])
            self.genesis_created = True
            current_index = 1
            
            print ("Genesis Block with index " + str(current_index) +" added at " + str(datetime.utcnow()) + " to the chain \n")
        
        return self.genesis
    
    def proof_of_work(self,block):
        while block.hash.hexdigest()[:4] != '0000':
            block.proof += 1
            block.hash_data()
        
        print ("Validated proof: "+str(block.proof))
        return True 

    @property
    def last_block(self):
        lastblock = self.blockchain[-1]
        return lastblock

    def resolve(self):
        for tempblock in self.blockchain:
            #check for where the fork is
            if len(tempblock) != 1:
                print ("Forking detected")
                for forkchain in range(0,len(tempblock)-1):
                    #check which chain is longer
                    current_longestchain = []
                    if len(forkchain) > len(current_longestchain):
                        current_longestchain = forkchain
                    print (current_longestchain)
                    return current_longestchain



class Block:
    def __init__(self, txnlist):
        self.txnlist = txnlist
        #Header
        # Set these values from blockchain 
        self.pre_hash = None
        self.index = None    

        # Set when block is created
        self.proof = 0
        self.merkle_root = self.build_tree()
        self.timestamp = time.time()

        #Hash data
        self.hash = None
        

    def hash_data(self):
        hashed = hashlib.sha256()
        hashed.update(str(self.pre_hash).encode('utf-8')+str(self.timestamp).encode('utf-8')+str(self.proof).encode('utf-8')+str(self.merkle_root).encode('utf-8'))
        self.hash = hashed
        return hashed
    

    def build_tree(self):
        mt = MerkleTree(self.txnlist)
        buildtree= mt.build()
        merkleroot = mt.root
        self.merkle_root = merkleroot
        return merkleroot
