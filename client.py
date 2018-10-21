from ecdsa import SigningKey, NIST192p
from transaction import Transaction


class SPVClient:
    def __init__(self,blockchain,cid):
        self.blockchain = blockchain

        # create key pair/generate wallet for client
        self.privatekey = SigningKey.generate(curve=NIST192p)
        self.publickey = self.privatekey.get_verifying_key()
        
        self.cid = cid
        self.addr = self.getAddrBalance()
        
    def getAddrBalance(self):
        addr = {}
        accountlist = list(addr.keys())
        for block in self.blockchain.blockchain:
            for transaction in block.txnlist:
                data = json.loads(transaction)
               
                if data['sender'] not in accountlist:
                    accountlist.append(data['sender'])
                    addr.update({str(data['sender']):data['amount']})
                elif data['receiver'] not in accountlist:
                    accountlist.append(data['receiver'])
                    addr.update({str(data['receiver']):data['amount']})
                else:
                    balance_tominus = addr.get(data['sender']) - data['amount']
                    addr.update({str(data['sender']):balance_tominus})
                    balance_toadd = addr.get(data['receiver']) + data['amount']
                    addr.update({str(data['receiver']):balance_toadd}) 

        self.addr = addr
        return self.addr
 
    def new_txn(self,recipient, amount, comment):
        # send signed transactions
        if self.balance > 0:
            senderkey = self.publickey
            newTxn = Transaction(senderkey.to_string().hex(), recipient, amount,comment)
            toJson = newTxn.to_json() 
            signed = newTxn.sign(toJson, sk.to_string())
            self.blockchain.transactionpool.append(newTxn.to_json())
            print ("\nClient "+str(self.cid)+" Added Transaction to transaction pool \n", self.blockchain.transactionpool)
            return self.blockchain.transactionpool
        else:
            print ("\nClient "+str(self.cid)+" does not have enough coins to make a transaction")
            return self.blockchain.transactionpool

    def retrieve_block_headers(self):
        blockheaders = []
        for block in self.blockchain.blockchain:
            blockheaders.append(block.hash)
        
        print("\nBlockheaders: ",blockheaders)
        return blockheaders
          
