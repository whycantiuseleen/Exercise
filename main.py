from transaction import Transaction
from blockchain import Blockchain, Block
from ecdsa import SigningKey, NIST192p
from merkletree import MerkleTree
from miner import Miner
from client import SPVClient

def test():
    ## Generate Key
    sk = SigningKey.generate(curve = NIST192p)
    vk = sk.get_verifying_key()

    ## Create Transactions
    newTxn = Transaction(vk.to_string().hex(), 'receiverkey', 100)
    ## convert to JSON
    toJson = newTxn.to_json()
    #print (toJson)
    
    ## Sign JSON
    signature = newTxn.sign(toJson, sk.to_string())
    # print (signed)
    
    ## Validate
    validated = newTxn.validate_signature(toJson, signature, vk.to_string())
    #print ("Transaction validity: ", validated)

    sk2 = SigningKey.generate(curve = NIST192p)
    vk2 = sk2.get_verifying_key()

    txn1 = Transaction(vk.to_string().hex(),'receiverkey1', 100).to_json()
    transactionlist = [txn1]

    ##Create Block with transaction
    block = Block(transactionlist)
   
    chain = Blockchain()
    chain.set_blockheader(block)

    ##Populate blockchain with blocks
    for i in range(2):
        chain.set_blockheader(block)
        chain.add(block,1)

    txn4 = Transaction('receiverkey1','receiverkey3', 100).to_json()
    txn5 = Transaction('receiverkey3','receiverkey1', 100).to_json()
   
    chain.transactionpool.append(txn4)
    chain.transactionpool.append(txn5)

    ## Miner Test
    m1 = Miner(chain)
    block4 = m1.mine()
    chain.add(block4,m1.publickey.to_string().hex())
    block5 = m1.mine()
    chain.add(block5,m1.publickey.to_string().hex())

    m2 = Miner(chain)
    block6 = m2.mine()
    block6_2 = m1.mine()
    chain.fork(block6,block6_2,m1.publickey.to_string().hex(),m2.publickey.to_string().hex())
    m1.mine()
    
if __name__ == '__main__':
    test()