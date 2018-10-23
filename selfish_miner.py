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

    def foundByMe(self, chain):
        peers = chain.peers
        longest_chain = None
        currentLen = len(chain) + 1 #seeing if this new found block makes my pub chain longest

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

    def mine(self):
        self.getAddrBalance()

        # Blockchain obj
        currentchain = self.blockchain
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

    def selfish_mine(self, chain):
        # state = 0

        # publicLongestLen = 0
        #num of blocks mined privately
        privateBlockLen = 0
        lenDiff = 0

        private_blocks = []
        public_chain = chain.blockchain
        private_chain = chain.blockchain

        # #start mining normally
        # txn_pool = private_chain.transactionpool
        # #verify txns
        # verified_txns = self.check_transaction(txn_pool)
        #
        # new_block = Block(verified_txns)
        new_block = self.mine(private_chain)

#######below is following the selfish mining algo. Please help check if its correct

        #if mine is actually longest aft checking
        if foundByMe(private_chain):
            lenDiff = len(private_chain) - len(public_chain)
            private_chain.append([new_block])
            privateBlockLen += 1
            private_blocks.append(new_block)
#need publich/ braodcast?
            if lenDiff == 0 and privateBlockLen == 2:
                for i in range(len(private_blocks)):
                    #publish to the public chain?
                    public_chain.append(private_blocks[i])
                privateBlockLen = 0
            another_block = self.mine(private_chain)
        else:
            lenDiff = len(private_chain) - len(public_chain)
            public_chain.append(new_block)
            if lenDiff == 0:
                private_chain = public_chain
                privateBlockLen = 0
            elif lenDiff == 1:
                public_chain.append(private_chain[len(private_chain)-1])
            elif lenDiff == 2:
                for i in range(len(private_blocks)):
                    #publish to the public chain?
                    public_chain.append(private_blocks[i])
                privateBlockLen = 0
            else:
                public_chain.append(private_blocks[0])

            another_block = self.mine(private_chain)

        return private_blocks

        #A round begin when the state=0 and finish when we return to it
        # for i in range(N_events):
        #     r = random.random()
        #
        #     if state==0:
        #         #Initial State.
        #         #The selfish miners have 0 hidden block.
        #         if r<=alpha:
        #             #The selfish miners found a block.
        #             #They don't publish it.
        #             print('1st round')
        #             state=1
        #         else:
        #             #The honest miners found a block.
        #             #The round is finished : the honest miners found 1 block
        #             # and the selfish miners found 0 block.
        #             LongestChainLength+=1
        #             state=0
        #             print('no happy')
        #
        #     elif state==1:
        #         #There is one hidden block in the pocket of the selfish miners.
        #         if r<=alpha:
        #             #The selfish miners found a new block.
        #             #It remains hidden.
        #             #The selfish miners are now two blocks ahead.
        #             #The two blocks are hidden.
        #             state=2
        #             n=2
        #             print('2nd round')
        #         else:
        #             state=-1
        #
        #     elif state==-1:
        #         #It's the state 0' in the paper of Eyal and Gun Sirer
        #         #The honest miners found a block.
        #         #So the selfish miners publish their hidden block.
        #         #The blockchain is forked with one block in each fork.
        #         if r<=alpha:
        #             #the selfish miners found a block in their fork.
        #             #The round is finished : Selfish miners won 2 blocks and the honest miners 0.
        #             NumberOfSelfishMineBlock+=2
        #             LongestChainLength+=2
        #             state=0
        #             print('1st round again')
        #         elif r<=alpha+(1-alpha)*gamma:
        #             #The honest miners found a block in the fork of the selfish miners.
        #             #The round is finished : Selfish miners won 1 blocks and the honest miners 1.
        #             NumberOfSelfishMineBlock+=1
        #             LongestChainLength+=2
        #             state=0
        #             print('1st round weww')
        #         else:
        #             #The honest miners found a block in their fork.
        #             #The round is finished : Selfish miners won 0 blocks and the honest miners 2.
        #             NumberOfSelfishMineBlock+=0
        #             LongestChainLength+=2
        #             state=0
        #             print('1st round oops')
        #
        #     elif state==2:
        #         #The selfish miners have 2 hidden blocks in their pocket.
        #         if r<=alpha:
        #             #The selfish miners found a new hidden block
        #             n+=1
        #             state=3 #can already set state = 0
        #             print('hahaha')
        #         else:
        #             #The honest miners found a block.
        #             #The selfish miners are only one block ahead of the honest miners,
        #             #So they publish their chain which is of length n.
        #             #The round is finished : Selfish miners won n blocks and the honest miners 0.
        #             LongestChainLength+=n
        #             NumberOfSelfishMineBlock+=n
        #             state=0
        #             print('ok enuf')
        #     elif state>2:
        #         if r<=alpha:
        #             #The selfish miners found a new hidden block
        #             n+=1
        #             state += 1 #or state=0, SM broadcast his 2 blocks ahead, round finished
        #             print('woww')
        #         else:
        #             #The honest miners found a block
        #             #The selfish miners publish one of their hidden block
        #             # and are losing one point in the run.
        #             state -= 1
        #             print('uhohh')

                    #proportion of blocks selfishly mined and its length
        #return float(NumberOfSelfishMineBlock)/LongestChainLength, NumberOfSelfishMineBlock, LongestChainLength-NumberOfSelfishMineBlock, state


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
