# 50.037-Blockchain

- Updating -

Simulation of Blockchain concepts with python language

Modules
1. Transaction.py
- to_json
  - Convert data structure into json format
- sign
  - Allows individuals to sign the transaction that they have made which can be used for verification by the miners later.
- validate_signature
  - validates the signature that is tied to the transaction.
 
2. Merkletree.py
- get_root
  - Obtain the hash of the root element of the merkletree
- get_proof
  - Get Merklepath to be used for validation of a transaction by SPVClients(lightweight nodes)
- verify_proof
  - verify the merklepath.
- build
  - build a merkle tree based on the transactions that is mined in the transactionpool.

3. Blockchain.py
- validate_block
  - Ensures that the prehash value of the new block is equals to the hashvalue of the previous block.
- set_blockheader
  - set blockheader which consists of the prehash, index, merkleroot

4. Miner.py
5. Client.py
6. Simulation.py
