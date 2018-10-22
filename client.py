from ecdsa import SigningKey, NIST192p
from transaction import Transaction
from merkletree import MerkleTree
from collections import OrderedDict
from blockchain import Blockchain,Block
import hashlib,json


class SPVClient:
    def __init__(self):
        # create key pair/generate wallet for client
        self.privatekey = SigningKey.generate(curve=NIST192p)
        self.publickey = self.privatekey.get_verifying_key()
     
    def new_txn(self, recipient, amount):
        # Make txn, don't need to check if the balance is correct cos miner will check when they mine
        senderkey = self.publickey.to_string().hex()
       
        newTxn = Transaction(senderkey, recipient, amount)
        signedTxn = newTxn.sign(newTxn, self.privatekey.to_string())
        self.blockchain.transactionpool.append(newTxn.to_json)
        print ("\nClient "+str(senderkey)+" Added Transaction to transaction pool \n", self.blockchain.transactionpool)
        
        return signedTxn 

    def retrieve_block_headers(self, provider):
        blockheaders = []
        headers = {}
        chain = provider.blockchain.blockchain
        for block in chain:
            headers = block[0].get_header()
            blockheaders.append(headers)

        # print("\nBlockheaders: ",blockheaders)
        return blockheaders
          
    def receive_transaction(self, txn, minernode):
        # Receive blockheader from fullnode
        # Receive merkle path
        # Check with fullnode on which block contains transaction
        hashedTxn = hashlib.sha512(txn.encode('utf-8')).hexdigest()    
        blockheaders = self.retrieve_block_headers(minernode)
        # print ("Tochecktxn: ",hashedTxn,'\n')
        proof = minernode.get_merklepath(txn)
        # Verify whether there is a merkleroot that corresponds in header
        flag = None
        for hashedheader in blockheaders:
            merkleroot = hashedheader.get('merkleroot')
            flag = MerkleTree.verify_proof(hashedTxn, proof, merkleroot)
        
            if flag == True:
                print ("\nTransaction is verified and found in the blockchain")
                break
            else: 
                print ("\nTransaction not found in blockchain")
        
        return flag
            

        