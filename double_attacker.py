from blockchain import Blockchain, Block
from transaction import Transaction
from datetime import datetime
from merkletree import MerkleTree
from ecdsa import SigningKey, NIST192p
import json
from selfish_miner import SelfishMiner

class DoubleSpender:
    def __init__(self, blockchain):
        self.blockchain = blockchain

        # wallet
        self.privatekey = SigningKey.generate(curve=NIST192p)
        self.publickey = self.privatekey.get_verifying_key()

        # Address book of txn
        self.addr = {}

    def getAddrBalance(self,chain):
        addr = {}
        accountlist = list(addr.keys())
        for block in chain.blockchain:
            for transaction in block[0].txnlist:
                data = json.loads(transaction)
                if data['sender'] in accountlist:
                    balance_tominus = addr.get(data['sender']) - data['amount']
                    addr.update({str(data['sender']):balance_tominus})
                    if data['receiver'] in accountlist:
                        balance_toadd = addr.get(data['receiver']) + data['amount']
                        addr.update({str(data['receiver']):balance_toadd})
                    elif data['receiver'] not in accountlist:
                        accountlist.append(data['receiver'])
                        addr.update({str(data['receiver']):data['amount']})

                else:
                    accountlist.append(data['sender'])
                    addr.update({str(data['sender']):-data['amount']})

                    if data['receiver'] in accountlist:
                        balance_toadd = addr.get(data['receiver']) + data['amount']
                        addr.update({str(data['receiver']):balance_toadd})
                    elif data['receiver'] not in accountlist:
                        accountlist.append(data['receiver'])
                        addr.update({str(data['receiver']):data['amount']})
        # print (addr)
        self.addr = addr
        return addr

    def get_balance(self, chain, pk):
        addr = self.getAddrBalance(chain)
        # account_keys = list(addr.keys)
        for k in addr.keys():
            if k == pk:
                return addr[k]

    def check_transactions(self,transactionpool):
        # Check Signature
        # Check if the sender has enough coins to send
        verifiedpool = []
        addrbk_checked = self.addr
        accountlist = list(addrbk_checked.keys())
        for transaction in transactionpool:
            # Cost of transaction
            print(transaction)
            pool_data = json.loads(transaction)
            cost = pool_data['amount']
            sender = pool_data['sender']
            # Amt that sender has
            amt_onhand = addrbk_checked.get(sender)

            if sender not in accountlist:
                # print (str(sender) + " not in account list, transaction rejected")
                continue

            else:
                # print ('Amount on hand in addrbk', amt_onhand)
                if amt_onhand > cost:
                    balance = amt_onhand - cost
                    addrbk_checked.update({pool_data['sender']:balance})
                    verifiedpool.append(transaction)
                    # print ("Transaction is valid\n")


        return verifiedpool

    def new_txn(self, recipient, amount):
        self.getAddrBalance(self.blockchain)
        senderkey = self.publickey.to_string().hex()
        balance = self.addr.get(senderkey)
        if balance > 0:
            newTxn = Transaction(senderkey, recipient, amount)
            # signedTxn = newTxn.sign(newTxn, self.privatekey.to_string())
            self.blockchain.transactionpool.append(newTxn.to_json())
            #after spend immediately mine
            # first_block = self.mine(self.blockchain)
            print ("\nMiner "+str(senderkey)+" Added Transaction to transaction pool \n", self.blockchain.transactionpool)
        else:
            print ('\nMiner '+str(senderkey)+" does not have sufficient coins to send a transaction")
        return newTxn.to_json()

    def attack(self, chain):
        public_chain = chain

        #fork current chain status to his private chain
        private_chain = chain

        #first txn to a random merchant
        first_txn= self.new_txn('receiver1', 10)
        #he mines the block with that txn
        publicBlock = self.mine(public_chain)
        #update nomrally to the public version of the chain
        public_chain.add(publicBlock, self.publickey.to_string().hex())

        #make second txn to another since first one is approved
        second_txn = self.new_txn('receiver2', 10)
        privBlock = self.mine(private_chain)
        private_chain.add(privBlock, self.publickey.to_string().hex())

        # start growing his private chain using selfish mining
        privateBlocks = SelfishMiner.selfish_mine(self, private_chain)

        # publish his work when its longer
        for i in range(len(privateBlocks)):
            public_chain.add(privateBlocks[i], self.publickey.to_string().hex())

        print("Miner has performed a double attack\n")

    def mine(self, currentchain):
        self.getAddrBalance(currentchain)

        # Blockchain obj
        transactionpool = currentchain.transactionpool
        # Check Transactions
        verifiedpool = self.check_transactions(transactionpool)

        print ("\nMining Transaction, current number of block is: "+ str(len(currentchain.blockchain)))
        # Create block object
        newblock = Block(verifiedpool)
        currentchain.set_blockheader(newblock)

        proof = currentchain.proof_of_work(newblock)
        print ("\nMiner " + str(self.publickey.to_string().hex())+" found new block")
        return newblock


    def get_merklepath(self, txn):
        # Get Tree information from minernode
        proof = None
        for block in self.blockchain.blockchain:
            if txn in block[0].txnlist:
                merkletree = MerkleTree(block[0].txnlist)
                merkletree.build()
                arrayTree = merkletree.tree

                # Get merkle path
                proof = merkletree.get_proof(txn)

        return proof
