import pyhop2


"""Helper Functions"""

def get_block_above(state, block):
    if state.clear[block]: return None
    for stack in state.stacks:
        if block in stack:
            return stack[stack.index(block)+1]


def get_stack_of_block(state, block):
    for i in range(len(state.stacks)):
        if block in state.stacks[i]: return i
    return -1

def remove_from_stack(state, block):
    state.stacks[get_stack_of_block(state, block)].remove(block)

def first_empty_stack(state):
    for i in range(len(state.stacks)):
        if is_empty(state, i): return i
    return -1

def is_empty(state, stack_index):
    return state.stacks[stack_index] == []

"""
Actions:
    stack
    unstack
    restack
    move_to_stack
"""



"""moves a block from the table to a clear block"""
def stack(state, block, dest):
    if state.pos[block] == 'table' and state.clear[block] and state.clear[dest]:
        remove_from_stack(state,block)
        state.stacks[get_stack_of_block(state, dest)] += [block]
        state.pos[block] = dest
        state.clear[dest] = False
        return state


"""moves a block on another block to the table"""
def unstack(state, block, position):
    if state.pos[block] == position and position != 'table' and state.clear[block]:
        empty_stack = first_empty_stack(state)
        if empty_stack == -1:
            return None
        remove_from_stack(state, block)
        state.pos[block] = 'table'
        state.stacks[empty_stack] += [block]
        state.clear[position] = True
        return state


"""moves a block from one block to a different clear block"""
def restack(state, block, position, dest):
    if state.pos[block] == position and position != 'table' and state.clear[block] and state.clear[dest]:
        remove_from_stack(state, block)
        state.pos[block] = dest
        state.stacks[get_stack_of_block(state, dest)] += [block]
        state.clear[position] = True
        state.clear[dest] = False
        return state


"""moves any clear block to the top of a stack specified by stack index"""
def move_to_stack(state, block, stack_index):
    position = state.pos[block]
    if state.clear[block]:
        remove_from_stack(state, block)
        if position != 'table': state.clear[position] = True
        dest = 'table'
        if not is_empty(state, stack_index): 
            dest = state.stacks[stack_index][-1]
            state.clear[dest] = False
        state.pos[block] = dest
        state.stacks[stack_index] += [block]
        return state
                

"""incorporating these actions into the planner"""
pyhop2.declare_actions(move_to_stack, stack, unstack, restack)