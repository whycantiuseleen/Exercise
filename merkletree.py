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
        # Only works for binary tree
        proof = []
        level = 0
        tree = self.tree
        currentIndex = self.transactionlist.index(hashedtxn)    
        
        while level < len(tree)-1:
            if level == 0:
                if len(tree[level])%2 != 0:
                    tree[level].append(tree[level][-1])

                if currentIndex == 0:
                    hashvalue = tree[level][1]
                    proof.append({'right':hashvalue})
                elif currentIndex%2 != 0:
                    # ODD Index - return Left Child
                    hashvalue = tree[level][currentIndex-1]
                    proof.append({'left':hashvalue})
                else:
                    # EVEN Index - return Right Child
                    hashvalue = tree[level][currentIndex+1]
                    proof.append({'right':hashvalue})
                # print ("Hashvalueobtained: ",hashvalue)

            else:
                hashIndex = int(currentIndex/2)
                
                if len(tree[level])%2 != 0:
                    tree[level].append(tree[level][-1])

                if hashIndex == 0:
                    hashvalue = tree[level][1]
                    proof.append({'right':hashvalue})
                elif hashIndex%2 != 0:
                    # ODD index
                    hashvalue = tree[level][hashIndex-1]
                    proof.append({'left':hashvalue})
                else:          
                    # EVEN index
                    hashvalue = tree[level][hashIndex+1]
                    proof.append({'right':hashvalue})
                # print ("Hashvalueobtained2: ",hashvalue)
                # Set new index
                currentIndex = hashIndex
            
            level +=1 

        # print ("\nMerkle path: ",proof)
        return proof

    def verify_proof(hashedtxn, proof, root):   
        # print ('\nVerifying Transaction ') 
      
        if len(proof) == 0:
            return hashedtxn == root
        else:
            hashedData = hashedtxn
            count = 0
            for dictproof in proof:
                count += 1
                # print ("Count: ",count)
                # print ("Hasheddata: ",hashedData)
                position = list(dictproof.keys())
                data = list(dictproof.values())
                # print ("POSITION, DATA: ",position[0],data[0])
                if position[0] == 'left':
                    combined_tohash = str(data[0])+str(hashedData)
                    hashedData = hashlib.sha512(combined_tohash.encode('utf-8')).hexdigest()
                    
                else:                
                    combined_tohash = str(hashedData)+str(data[0])
                    hashedData = hashlib.sha512(combined_tohash.encode('utf-8')).hexdigest()
        
        return root == hashedData

    def build(self):
        leaf_hashes = []
        tree = []
        oddNum = False
        txnlist = self.transactionlist

        # print ("list ",txnlist)
        for transaction in txnlist:
            # print ('test')
            hashed_data = hashlib.sha512(transaction.encode('utf-8')).hexdigest()
            leaf_hashes.append(hashed_data)

        tree.append(leaf_hashes)            
    
        current_level = leaf_hashes
        nodes_remaining = len(current_level)
        # print ("Currentlvl", current_level)
        
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
