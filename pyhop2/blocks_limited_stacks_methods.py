import pyhop2
from blocks_limited_stacks_actions import *

"""
Main Tasks: 
    'move_one'
    'make_clear'
Methods: 
    make_clear_dump_nbr
    make_clear_dump_smallest
    make_clear_distribute
    make_clear_split_nbr
    make_clear_split_smallest
Helpers:
    make_clear_dump
    make_clear_split
    make_clear_distribute_aux
    get_block_above    
"""

def get_block_above(state, block):
    """
    returns the index of the stack that the block is in
    in the state.stacks representation.
    """
    if state.clear[block]: return None
    for stack in state.stacks:
        if block in stack:
            return stack[stack.index(block)+1]


def m_make_clear_dump(state, b1, b2, dump_index):
    """
    places all blocks above b1 on top of the stack
    with index dump_index, moving each block from the top,
    one by one.
    """
    if state.clear[b1]:
        return []
    b_above = get_block_above(state, b1)
    return [('make_clear_dump', b_above,b2,dump_index), 
            ('move_to_stack', b_above, dump_index)]

def m_make_clear_dump_to_smallest(state, b1, b2):
    """
    dumps all blocks above b1 onto the smallest stack
    which doesn't contain b2 (moving each block one
    at a time).
    """
    num_stacks = len(state.stacks)
    if num_stacks < 3: return None
    b1_stack = get_stack_of_block(state, b1)
    b2_stack = get_stack_of_block(state, b2)
    smallest = None

    for i in range(num_stacks):
        if i == b1_stack or i == b2_stack: 
            continue
        if not smallest: 
            smallest = i
        if len(state.stacks[i]) <= len(state.stacks[smallest]): 
            smallest = i

    return[('make_clear_dump', b1, b2, smallest)]

def m_make_clear_dump_to_nbr(state, b1, b2):
    """
    finds the closest neighboring stack
    to b1's stack which also don't contain b2. It then
    uses make_clear_dump to dump everything above
    b1 onto that neighbor.
    """
    num_stacks = len(state.stacks)
    if num_stacks < 3: return None
    b1_stack = get_stack_of_block(state, b1)
    b2_stack = get_stack_of_block(state, b2)
    nbr = None
    left_nbr = (b1_stack - 1) % num_stacks
    right_nbr = (b1_stack + 1) % num_stacks
    
    return [('make_clear_dump', b1 ,b2, left_nbr if left_nbr != b2_stack else right_nbr)]

def m_make_clear_distribute(state, b1, b2):
    """
    Uses aux method to distribute all the blocks above b1
    to all the other stacks which also don't contain b2.
    """
    return [('make_clear_distribute_aux', b1, b2, get_stack_of_block(state,b1))]

def m_make_clear_distribute_aux(state, b1, b2, dest_stack_index):
    """
    Distributes the blocks on top of b1 across all other stacks
    other than the stack of b2.
    """
    if state.clear[b1]:
        return []
    b1_stack = get_stack_of_block(state, b1)
    b2_stack = get_stack_of_block(state, b2)

    if dest_stack_index == b1_stack: dest_stack_index += 1
    dest_stack_index %= len(state.stacks)
    if dest_stack_index == b2_stack: dest_stack_index += 1
    dest_stack_index %= len(state.stacks)
    if dest_stack_index == b1_stack: dest_stack_index += 1
    dest_stack_index %= len(state.stacks)

    b_above = get_block_above(state, b1)
    return [('make_clear_distribute_aux', b_above, b2, dest_stack_index + 1),
            ('move_to_stack', b_above, dest_stack_index)] 

def m_make_clear_split_to_nbr(state, b1, b2):
    """
    finds closest left and right neighboring stacks which also
    don't contain b2, then alternates placing blocks on those 
    two neighbors.
    """
    num_stacks = len(state.stacks)
    if num_stacks < 4: return None

    b1_stack = get_stack_of_block(state, b1)
    b2_stack = get_stack_of_block(state, b2)
    left_stack = None
    right_stack = None

    curr_stack = (b1_stack - 1) % num_stacks
    while curr_stack != b1_stack:
        if curr_stack != b2_stack:
            left_stack = curr_stack
            break
        curr_stack = (curr_stack - 1) % num_stacks

    curr_stack = (b1_stack + 1) % num_stacks
    while curr_stack != b1_stack:
        if curr_stack != b2_stack:
            right_stack = curr_stack
            break
        curr_stack = (curr_stack + 1) % num_stacks
    
    return [('make_clear_split', b1, b2, left_stack, right_stack, True)]

def m_make_clear_split_to_smallest(state, b1, b2):
    """
    finds the two smallest stacks which don't contain
    b1 or b2, then alternates placing blocks onto those 
    shortest stacks
    """
    num_stacks = len(state.stacks)
    if(num_stacks < 4): return None
    b1_stack = get_stack_of_block(state, b1)
    b2_stack = get_stack_of_block(state, b2)
    
    #finding the smallest 2 stacks which don't contain b1 or b2
    small_stack1 = None
    small_stack2 = None
    for i in range(num_stacks):
        if i == b1_stack or i == b2_stack:
            continue
        if not small_stack1:
            small_stack1 = i
            small_stack2 = i
        if len(state.stacks[i]) <= len(state.stacks[small_stack2]):
            small_stack2 = i
        if len(state.stacks[small_stack2]) <= len(state.stacks[small_stack1]):
            temp = small_stack1
            small_stack1 = small_stack2
            small_stack2 = temp
    return [('make_clear_split', b1, b2, small_stack1, small_stack2, True)]
    
def m_make_clear_split(state, b1, b2, stack1, stack2, iter_even : bool):
    """ 
    workhorse split method. It alternates placing blocks above b1
    onto the stack1 and stack2.
    """
    if state.clear[b1]:
        return []
    b_above = get_block_above(state, b1)
    return[('make_clear_split', b_above, b2, stack1, stack2, not iter_even), 
            ('move_to_stack', b_above, stack1 if iter_even else stack2)]

dummy_block = 'DUMMY_BLOCK'

"""
    The dummy block is used for convenience.
    It is used so the methods for make_clear can also be 
    used to clear an entire stack from the table. We can't
    do ('make_clear', 'table') with the current setup. 
    Unfortunately, removing dummy blocks requires applying an 
    action which may saffect costs.
"""
def remove_dummy(state):
    """ 
    Removes the dummy_block from the state.
    This must be used anytime after the dummy_block 
    is used to clear a stack.
    """
    for stack in state.stacks:
        if dummy_block in stack: 
            stack.remove(dummy_block)
            state.clear.pop(dummy_block, None)
            state.pos.pop(dummy_block, None)
        if len(stack) > 0:
            state.pos[stack[0]] = 'table'
    return state
    return []

def insert_dummy(state, stack):
    bottom = None
    if state.stacks[stack]: 
        bottom = state.stacks[stack][0]
    state.stacks[stack].insert(0, dummy_block)
    if bottom:
        state.pos[bottom] = dummy_block
        state.clear[dummy_block] = False
    state.pos[dummy_block] = 'table'
    return state


pyhop2.declare_actions(insert_dummy, remove_dummy)

def m_dissolve_stack(state, stack):
    """
    This is used to clear a specified stack from the table.
    Note that it can use any of the clearing methods for blocks.
    """
    return [('insert_dummy', stack), ('make_clear', dummy_block, dummy_block), ('remove_dummy',)]

pyhop2.declare_task_methods('dissolve_stack', m_dissolve_stack)


def m_move_one(state, b1, dest):
    """
    This is a general move method which doesn't
    care if b1 is on the table or not or if
    dest is the table or a block.
    """
    start = state.pos[b1]
    if start == dest: return []
    elif start == 'table': return [('stack', b1, dest)]
    elif dest == 'table': return [('unstack', b1, start)]
    else: return [('restack', b1, start, dest)]


""" 
Adding all the above methods to the planner.
The main one to take note of is 'make_clear'.
"""
pyhop2.declare_task_methods('move_one', m_move_one)
pyhop2.declare_task_methods('make_clear', m_make_clear_distribute, 
    m_make_clear_split_to_nbr, m_make_clear_split_to_smallest, 
    m_make_clear_dump_to_nbr, m_make_clear_dump_to_smallest)
pyhop2.declare_task_methods('make_clear_dump', m_make_clear_dump)
pyhop2.declare_task_methods('make_clear_dump_to_nbr', m_make_clear_dump_to_nbr)
pyhop2.declare_task_methods('make_clear_dump_to_smallest', m_make_clear_dump_to_smallest)
pyhop2.declare_task_methods('make_clear_distribute', m_make_clear_distribute)
pyhop2.declare_task_methods('make_clear_distribute_aux', m_make_clear_distribute_aux)
pyhop2.declare_task_methods('make_clear_split', m_make_clear_split)
pyhop2.declare_task_methods('make_clear_split_to_nbr', m_make_clear_split_to_nbr)
pyhop2.declare_task_methods('make_clear_split_to_smallest', m_make_clear_split_to_smallest)
