import random

#this class is to illustrate concept of selfish mining


class SelfishMining():
    def selfish_mine(alpha, gamma, N_events):
            state=0
            LongestChainLength=0
            NumberOfSelfishMineBlock=0

            #A round begin when the state=0 and finish when we return to it
            for i in range(N_events):
                r = random.random()

                if state==0:
                    #Initial State.
                    #The selfish miners have 0 hidden block.
                    if r<=alpha:
                        #The selfish miners found a block.
                        #They don't publish it.
                        print('1st round')
                        state=1
                    else:
                        #The honest miners found a block.
                        #The round is finished : the honest miners found 1 block
                        # and the selfish miners found 0 block.
                        LongestChainLength+=1
                        state=0
                        print('no happy')

                elif state==1:
                    #There is one hidden block in the pocket of the selfish miners.
                    if r<=alpha:
                        #The selfish miners found a new block.
                        #It remains hidden.
                        #The selfish miners are now two blocks ahead.
                        #The two blocks are hidden.
                        state=2
                        n=2
                        print('2nd round')
                    else:
                        state=-1

                elif state==-1:
                    #It's the state 0' in the paper of Eyal and Gun Sirer
                    #The honest miners found a block.
                    #So the selfish miners publish their hidden block.
                    #The blockchain is forked with one block in each fork.
                    if r<=alpha:
                        #the selfish miners found a block in their fork.
                        #The round is finished : Selfish miners won 2 blocks and the honest miners 0.
                        NumberOfSelfishMineBlock+=2
                        LongestChainLength+=2
                        state=0
                        print('1st round again')
                    elif r<=alpha+(1-alpha)*gamma:
                        #The honest miners found a block in the fork of the selfish miners.
                        #The round is finished : Selfish miners won 1 blocks and the honest miners 1.
                        NumberOfSelfishMineBlock+=1
                        LongestChainLength+=2
                        state=0
                        print('1st round weww')
                    else:
                        #The honest miners found a block in their fork.
                        #The round is finished : Selfish miners won 0 blocks and the honest miners 2.
                        NumberOfSelfishMineBlock+=0
                        LongestChainLength+=2
                        state=0
                        print('1st round oops')

                elif state==2:
                    #The selfish miners have 2 hidden blocks in their pocket.
                    if r<=alpha:
                        #The selfish miners found a new hidden block
                        n+=1
                        state=3 #can already set state = 0
                        print('hahaha')
                    else:
                        #The honest miners found a block.
                        #The selfish miners are only one block ahead of the honest miners,
                        #So they publish their chain which is of length n.
                        #The round is finished : Selfish miners won n blocks and the honest miners 0.
                        LongestChainLength+=n
                        NumberOfSelfishMineBlock+=n
                        state=0
                        print('ok enuf')
                elif state>2:
                    if r<=alpha:
                        #The selfish miners found a new hidden block
                        n+=1
                        state += 1 #or state=0, SM broadcast his 2 blocks ahead, round finished
                        print('woww')
                    else:
                        #The honest miners found a block
                        #The selfish miners publish one of their hidden block
                        # and are losing one point in the run.
                        state -= 1
                        print('uhohh')

                        #proportion of blocks selfishly mined and its length
            #return float(NumberOfSelfishMineBlock)/LongestChainLength, NumberOfSelfishMineBlock, LongestChainLength-NumberOfSelfishMineBlock, state
            return NumberOfSelfishMineBlock

def main():
    alpha=0.35 #hashing power selfish miner hv, 1-alpha will be the rest
    gamma=0.5 #probaility selfish miner wins a blk
    N=10**2 #no of mining events

    print("Theoretical probability :",(alpha*(1-alpha)**2*(4*alpha+gamma*(1-2*alpha))-alpha**3)/(1-alpha*(1+(2-alpha)*alpha)))
    print("Simulated probability and block length by SM and HM resp, state:", SelfishMining.selfish_mine(alpha,gamma,N))

main()
