import pyhop2
import numpy as np
import random
#import blocks_goal_splitting


def gen_blocks_state(num_blocks: int, stacking_likelihood: float, max_stacks, start_state=False):
    """ creating a list of procedurally named blocks """
    block_counter = 0
    blocks = [] 
    while(block_counter < num_blocks):
        blocks += [block_counter.__str__()]
        block_counter += 1

    """ initializing the random state to be developed and returned """
    state = pyhop2.State()
    state.pos = {}
    state.clear = {}
    state.max_stacks = max_stacks
    if num_blocks == 0 :
        return state
    state.pos[blocks[0]] = 'table'
    state.clear[blocks[0]] = True
    clear_blocks = [blocks[0]] #the set of blocks where state.clear[block] == True

    """
    Iterating through the blocks and putting the block on the table with probability
    (1 - stacking_probability).
    If the block is to be stacked, it is equally likely to be placed on any clear block 
    """
    table_counter = 1
    for block in blocks[1:] :
        observed = np.random.uniform(0,1)
        if observed > stacking_likelihood and table_counter < max_stacks :
            state.pos[block] = 'table'
            state.clear[block] = True
            clear_blocks += [block]
            table_counter += 1
        else :
            clear_index = random.randint(0, len(clear_blocks)-1) #choosing a random stack
            random_clear_block = clear_blocks[clear_index]       
            state.pos[block] = random_clear_block               
            state.clear[random_clear_block] = False              
            state.clear[block] = True
            #current block replaces random_clear_block in clear status
            clear_blocks[clear_index] = block

    permute_blocks(state)
    if start_state:
        state.stacks = gen_list_representation(state, max_stacks)

    return state                  
    
def permute_blocks(state):
    """
    randomly permuting the blocks so that each block is equally likely to be in any position.
    """
    blocks = list(state.pos.keys())
    reordering = np.random.permutation(blocks) #random reordering of the blocks
    permutation = {}
    inverse_permutation = {}

    #creating a permutation by aligning the list of blocks with its reordering
    for i in range( len(blocks) ):
        permutation[ blocks[i] ] = reordering[i]
        inverse_permutation[ reordering[i] ] = blocks[i]
    permutation['table'] = 'table'
    inverse_permutation['table'] = 'table'

    copy = state.copy()
    for block in blocks:
        state.pos[block] = inverse_permutation[ copy.pos[permutation[block]] ]
        state.clear[block] = copy.clear[ permutation[block] ]

def gen_list_representation(state, max_stacks):
    stacks = [] 
    for block in state.pos:
        if state.pos[block] == 'table':
            stacks.append([block])
    while True:
        terminate =True
        for block in state.pos:
            for stack in stacks:
                if state.pos[block] in stack and block not in stack:
                    stack.append(block)
                    terminate = False
        if terminate:
            break
    stacks += [[] for i in range(max_stacks - len(stacks))]
    assert len(stacks) == max_stacks
    return stacks



""" ================================= """
""" an example of using the generator """
""" ================================= """

def main():
    num_blocks = 7
    s0 = gen_blocks_state(num_blocks, .8, start_state=True) 
    print(s0.stacks)
    #s0.display()

    g = gen_blocks_state(num_blocks, .8)
    #g.display()

    goal = pyhop2.Multigoal('random goal')
    goal.pos = g.pos

    import sys
    sys.setrecursionlimit(400)
    print(pyhop2.find_plan(s0, [goal]))

#main()
