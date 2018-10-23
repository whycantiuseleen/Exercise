from blockchain import Blockchain, Block
from transaction import Transaction
from datetime import datetime
from ecdsa import SigningKey, NIST192p
import json

class SelfishMiner:
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

        #this can be used to check when network is connected, simil;ar to resolve()
    def foundByMe(self, chain):
        peers = chain.peers
        longest_chain = None
        currentLen = len(chain.blockchain) + 1 #seeing if this new found block makes my pub chain longest

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
            self.chain = longest_chain
            return True

        return False

    def mine(self, chain):
        self.getAddrBalance()

        transactionpool = chain.transactionpool
        # print("chain pool", chain.transactionpool)

        # Check Transactions
        verifiedpool = self.check_transactions(transactionpool)

        print ("\nMining Transaction, current number of block is: "+ str(len(chain.blockchain)))
        # Create block object
        newblock = Block(verifiedpool)
        chain.set_blockheader(newblock)

        proof = chain.proof_of_work(newblock)
        print ("\nMiner " + str(self.publickey.to_string().hex())+" found new block")
        return newblock

    def selfish_mine(self, chain):

        #num of blocks mined privately
        privateBlockLen = 0
        lenDiff = 0
        foundByMe = True #simplified, for demo's sake, otherwise need to run simulation/network to find out

        private_blocks = []
        public_chain = chain
        private_chain = chain

        new_block = self.mine(private_chain)

        #below is following the selfish mining algo. The test correct or not
        #depends on this

        #if mine is actually longest aft checking
        if foundByMe:
            lenDiff = len(private_chain.blockchain) - len(public_chain.blockchain)
            private_chain.add(new_block, self.publickey.to_string().hex())
            privateBlockLen += 1
            private_blocks.append(new_block)
#need publich/ braodcast?
            if lenDiff == 0 and privateBlockLen == 2:
                for i in range(len(private_blocks)):
                    #publish to the public chain?
                    public_chain.add(private_blocks[i], self.publickey.to_string().hex())
                privateBlockLen = 0
            another_block = self.mine(private_chain)
        else:
            lenDiff = len(private_chain.blockchain) - len(public_chain.blockchain)
            public_chain.add(new_block, self.publickey.to_string().hex())
            if lenDiff == 0:
                private_chain = public_chain
                privateBlockLen = 0
            elif lenDiff == 1:
                public_chain.append(private_chain[len(private_chain.blockchain)-1])
            elif lenDiff == 2:
                for i in range(len(private_blocks)):
                    #publish to the public chain?
                    public_chain.add(private_blocks[i], self.publickey.to_string().hex())
                privateBlockLen = 0
            else:
                public_chain.add(private_blocks[0], self.publickey.to_string().hex())

            another_block = self.mine(private_chain)

        return private_blocks

    def new_txn(self, recipient, amount, comment):
        if self.balance > 0:
            senderkey = self.publickey
            newTxn = Transaction(senderkey.to_string().hex(), recipient, amount,comment)
            # signedTxn = newTxn.sign(newTxn, self.privatekey.to_string())
            self.blockchain.transactionpool.append(newTxn.to_json)

            print ("\nMiner "+str(self.publickey.to_string().hex())+" Added Transaction to transaction pool \n", self.blockchain.transactionpool)
        else:
            print ('\nMiner '+str(self.publickey.to_string().hex())+" does not have any coin to send a transaction")
        return newTxn
