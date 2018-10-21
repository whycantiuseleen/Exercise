from blockchain import Blockchain, Block
from transaction import Transaction
from datetime import datetime
from ecdsa import SigningKey, NIST192p
import json

class Miner:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.newblock = None
        
        #wallet
        self.privatekey = SigningKey.generate(curve=NIST192p)
        self.publickey = self.privatekey.get_verifying_key()

        #Address book of txn
        self.addr = {}
       
    def getAddrBalance(self):
        addr = {}
        accountlist = list(addr.keys())
        for block in self.blockchain.blockchain:
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
    
    def check_transactions(self,transactionpool):
        # Check Signature
        # Check if the sender has enough coins to send
        verifiedpool = []
        addrbk_checked = self.addr
        accountlist = list(addrbk_checked.keys())
        for transaction in transactionpool:
            # Cost of transaction
            pool_data = json.loads(transaction) 
            cost = pool_data['amount']
            sender = pool_data['sender']
            # Amt that sender has
            amt_onhand = addrbk_checked.get(sender) 
            
            if sender not in accountlist: 
                print (str(sender) + " not in account list, transaction rejected")
            
            else: 
                # print ('Amount on hand in addrbk', amt_onhand)
                if amt_onhand > cost:
                    balance = amt_onhand - cost
                    addrbk_checked.update({pool_data['sender']:balance})
                    verifiedpool.append(transaction)
                    print ("Transaction is valid\n")
                else:
                    print ("Transaction is invalid\n")

        return verifiedpool

    def mine(self):
        self.getAddrBalance()

        # Blockchain obj
        currentchain = self.blockchain
        transactionpool = currentchain.transactionpool
        # Check Transactions
        verifiedpool = self.check_transactions(transactionpool)
        
        print ("\nMining Transaction, current number of block is: "+ str(len(currentchain.blockchain)))
        # Create block object
        newblock = Block(transactionpool)
        currentchain.set_blockheader(newblock)

        proof = currentchain.proof_of_work(newblock)
        print ("\nMiner " + str(self.publickey.to_string().hex())+" found new block")
        return newblock


    def new_txn(self, recipient, amount, comment):
        if self.balance > 0:
            senderkey = self.publickey
            newTxn = Transaction(senderkey.to_string().hex(), recipient, amount,comment)
            signedTxn = newTxn.sign(newTxn, self.privatekey.to_string())
            self.blockchain.transactionpool.append(newTxn.to_json)
            
            print ("\nMiner "+str(self.publickey.to_string().hex())+" Added Transaction to transaction pool \n", self.blockchain.transactionpool)
        else:
            print ('\nMiner '+str(self.publickey.to_string().hex())+" does not have any coin to send a transaction")
        return None