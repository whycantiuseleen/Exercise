import hashlib

class MerkleTree():
    def __init__(self, transactionlist):
        self.transactionlist = transactionlist
        self.tree = None
        self.root = None
    
    def get_root(self):
        root = self.root
        # print ("Root", root)
        return root

    def get_proof(self, hashedtxn):
        # Get index of transaction/2 round down.
        # Result is the index of the hash value to append inside
        proof = []
        level = 0
        tree = self.tree
        txnIndex = self.transactionlist.index(hashedtxn)
            
        while level < len(tree)-1:
            if level == 0:
                if txnIndex == 0:
                    hashvalue = tree[level][1]
                elif txnIndex%2 != 0:
                    # ODD Index - return Left Child
                    hashvalue = tree[level][txnIndex-1]
                    proof.append(hashvalue)
                else:
                    # EVEN Index - return Right Child
                    hashvalue = tree[level][txnIndex+1]
                    proof.append(hashvalue)

                level += 1
            else:
                hashIndex = int(txnIndex/2)
                hashvalue = tree[level][hashIndex]
                proof.append(hashvalue)

                # Set new index
                txnIndex = hashIndex
                level +=1 

        print ("Merkle path: ",proof)
        return proof

    def verify_proof(self, hashedtxn, proof, root):       
        if len(proof) == 0:
            return hashedtxn == root
        # else:
        #     for hashvalue in proof:
                

        return None
    def build(self):
        leaf_hashes = []
        tree = []
        oddNum = False
        txnlist = self.transactionlist

        #print ("list ",txnlist)
        for transaction in txnlist:
            #print (transaction)
            hashed_data = hashlib.sha512(transaction.encode('utf-8')).hexdigest()
            leaf_hashes.append(hashed_data)

        tree.append(leaf_hashes)            
    
        current_level = leaf_hashes
        nodes_remaining = len(current_level)
        #print ("Currentlvl", current_level)

        while nodes_remaining != 1:
           # print ("testloop")
            if len(current_level)%2 != 0:
                oddNum = True
            else:
                oddNum = False

            next_level = []
            if oddNum == False:
                for i in range(0,len(current_level)-1,2):
                    combined_tohash = str(current_level[i]) + str(current_level[i+1])
                    #print ("combined", combined_tohash)
                    new_hash = hashlib.sha512(combined_tohash.encode('utf-8')).hexdigest()
                    next_level.append(new_hash)
                current_level = next_level
                nodes_remaining = len(current_level)
                tree.append(current_level)
            else:
                ##if odd, take last node and hash with itself
                #print ("test oddloop")
                for i in range(0,len(current_level)-2,2):
                    #Hash up till last node
                    combined_tohash = str(current_level[i]) + str(current_level[i+1])
                    #print ("combined" , combined_tohash)
                    new_hash = hashlib.sha512(combined_tohash.encode('utf-8')).hexdigest()
                    next_level.append(new_hash)

                lastnode_tohash = str(current_level[-1]) + str(current_level[-1])
                lastnode_hash = hashlib.sha512(lastnode_tohash.encode('utf-8')).hexdigest()
                next_level.append(lastnode_hash)
                current_level = next_level
                nodes_remaining = len(current_level)
                tree.append(current_level)
        
        # print ("Merkle tree generated: \n")
        # for i in tree:
        #     print (i)

        
        self.tree = tree
        self.root = tree[-1][0]
        return tree
