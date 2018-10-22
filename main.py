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
    txn2 = Transaction(vk.to_string().hex(),'client1',100).to_json()
    txn3 = Transaction(vk2.to_string().hex(),'client3',100).to_json()
    txn4 = Transaction(vk2.to_string().hex(),'client4',100).to_json()
    transactionlist = [txn1,txn2,txn2,txn1,txn1,txn1,txn3]

    ##Create Block with transaction
    block = Block(transactionlist)
    block2 = Block([txn4])
    chain = Blockchain()
    chain.set_blockheader(block)
    chain.add(block,1)
    chain.set_blockheader(block2)
    chain.add(block2,2)

    ##Populate blockchain with blocks
    # for i in range(2):
    #     chain.set_blockheader(block)
    #     chain.add(block,1)
    
    # txn4 = Transaction('receiverkey1','receiverkey3', 100).to_json()
    # txn5 = Transaction('receiverkey3','receiverkey1', 100).to_json()
   
    # chain.transactionpool.append(txn4)
    # chain.transactionpool.append(txn5)

    # Miner Test
    m1 = Miner(chain)
    # block4 = m1.mine(chain)
    # chain.add(block4,m1.publickey.to_string().hex())
    # block5 = m1.mine(chain)
    # chain.add(block5,m1.publickey.to_string().hex())
 
    # m2 = Miner(chain)
    # block6 = m2.mine(chain)
    # block6_2 = m1.mine(chain)
    # chain.fork(block6,block6_2,m1.publickey.to_string().hex(),m2.publickey.to_string().hex())
   
    # chain.add(m2.mine(chain.resolve()),m2.publickey.to_string().hex())
    # print (chain.blockchain)
    
    spvclient = SPVClient()
    checktransaction = spvclient.receive_transaction(txn3,m1)

if __name__ == '__main__':
    test() 