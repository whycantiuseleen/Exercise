from transaction import Transaction
from blockchain import Blockchain, Block
from ecdsa import SigningKey, NIST192p
from merkletree import MerkleTree
from miner import Miner
from client import SPVClient
from selfish_miner import SelfishMiner
from double_attacker import DoubleSpender

def test():
    ## Generate Key
    sk = SigningKey.generate(curve = NIST192p)
    vk = sk.get_verifying_key()
    sk2 = SigningKey.generate(curve = NIST192p)
    vk2 = sk2.get_verifying_key()

    ## Create Transactions
    newTxn = Transaction(vk.to_string().hex(), 'receiverkey', 100)
    ## convert to JSON
    toJson = newTxn.to_json()
    ## Sign JSON
    signature = newTxn.sign(toJson, sk.to_string())
    print (signature)
    ## Validate
    validated = newTxn.validate_signature(toJson, signature, vk.to_string())

    txn1 = Transaction(vk.to_string().hex(),'receiverkey1', 100).to_json()
    txn2 = Transaction(vk.to_string().hex(),'client1',100).to_json()
    txn3 = Transaction(vk2.to_string().hex(),'client3',100).to_json()
    transactionlist = [txn1,txn2,txn3]

    ## Create Block with transaction
    block = Block(transactionlist)
    block2 = Block([txn3])
    chain = Blockchain()
    chain.set_blockheader(block)
    chain.add(block,1)
    chain.set_blockheader(block2)
    chain.add(block2,2)

    #Populate blockchain with blocks
    for i in range(2):
        chain.set_blockheader(block)
        chain.add(block,1)

    txn4 = Transaction('receiverkey1','receiverkey3', 100).to_json()
    txn5 = Transaction('receiverkey3','receiverkey1', 100).to_json()

    chain.transactionpool.append(txn4)
    chain.transactionpool.append(txn5)

    # Miner Test
    m1 = Miner(chain)
    m2 = Miner(chain)
    block4 = m1.mine(chain)
    chain.add(block4,m1.publickey.to_string().hex())
    block5 = m1.mine(chain)
    chain.add(block5,m1.publickey.to_string().hex())

    # SPV Test
    spvclient = SPVClient()
    checktransaction = spvclient.receive_transaction(txn3,m1)
    newtxn = spvclient.new_txn(m1.publickey.to_string().hex(),100)
    nt = m1.new_txn(spvclient.publickey.to_string().hex(),100)

    # print (nt)
    miners_list = [m1, m2]
    #selfish mine test
    m3 = SelfishMiner(chain)
    miners_list.append(m3)
    for miner in miners_list:
        block = miner.mine(chain)
        chain.add(block, miner.publickey.to_string().hex())

    # selfish_blocks = m3.selfish_mine(chain)
    # print(selfish_blocks)
    m4 = DoubleSpender(chain)

    txnToDS = m2.new_txn(m4.publickey.to_string().hex(), 60)
    chain.transactionpool.append(txnToDS)
    dsBlock = m4.mine(chain)
    chain.add(dsBlock, m4.publickey.to_string().hex())

    firsttxn = m4.new_txn(m1.publickey.to_string().hex(), 20)
    chain.transactionpool.append(firsttxn)
    print(chain.transactionpool)
    # m4.attack(chain)

    

if __name__ == '__main__':
    test()
