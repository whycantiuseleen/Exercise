import threading, time, json
from blockchain import Block, Blockchain
from transaction import Transaction
from miner import Miner
from client import SPVClient
from merkletree import MerkleTree

timetaken = {}
blockarray = []

client1 = SPVClient()
client2 = SPVClient()
client3 = SPVClient()

def initializechain():
    global txn4
    chain = Blockchain()

    txn4 = Transaction('ServerReward',client1.publickey.to_string().hex(),100).to_json()
    block = Block([txn4])
    chain.set_blockheader(block)
    chain.add(block,1)

    chain.transactionpool.append(txn4)

    return chain

def mine(mineride, chain):
    global timetaken
    global blockarray
    global miner

    miner = Miner(chain)
    minerID = miner.publickey.to_string().hex()
    print ("Miner " +str(minerID)+" mining")
    starttime = time.time()
    block = miner.mine(chain)
    elapsedtime = time.time() - starttime
    timetaken.update({minerID:elapsedtime})
    blockarray.append(block)

    return block

def addblock(chain):
    global blocktoadd
    global minerpk
    miners = list(timetaken.keys())
    timeElapsed = list(timetaken.values())

    shortestTime = timeElapsed[0]
    for time in timeElapsed:
        if time < shortestTime:
            shortestTime = time

    minerindex = timeElapsed.index(shortestTime)
    blocktoadd = blockarray[minerindex]
    minerpk = miners[minerindex]

    print ("\nMiner "+str(minerpk)+" found a block first")
    chain.set_blockheader(blocktoadd)
    chain.add(blocktoadd,minerpk)

    return chain

def newtransaction(chain):

    txn1 = client1.new_txn(client2.publickey.to_string().hex(),100)
    txn2 = client2.new_txn(client1.publickey.to_string().hex(),100)
    txn3 = client2.new_txn(client3.publickey.to_string().hex(),100)
    chain.transactionpool.append(txn1)
    chain.transactionpool.append(txn2)
    chain.transactionpool.append(txn3)

    return chain.transactionpool


def main():
    chain = initializechain()
    minerarray = []
    # 1st Concurrent Mining
    for i in range(3):
        thread = threading.Thread(target=mine, args=(i,chain))
        minerarray.append(thread)
        thread.start()

    for thread in minerarray:
        thread.join()

    addblock(chain)
    newtransaction(chain)
    # Mine new transactions made
    print ("Second round of mining")
    for i in range(3):
        thread = threading.Thread(target=mine, args=(i,chain))
        minerarray.append(thread)
        thread.start()

    for thread in minerarray:
        thread.join()

    addblock(chain)

    # Verify if transaction is in blockchain
    client1.receive_transaction(txn4,miner)

main()
