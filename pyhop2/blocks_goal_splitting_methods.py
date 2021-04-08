"""
Blocks World method definitions for blocks_goal_splitting_examples.
Author: Dana Nau <nau@umd.edu>
Feb 18, 2021
"""

import pyhop2


"""
Here are some helper functions that are used in the methods' preconditions.
"""

def is_done(b1,state,goal):
    if b1 == 'table': return True
    if b1 in goal.pos and goal.pos[b1] != state.pos[b1]:
        return False
    if state.pos[b1] == 'table': return True
    return is_done(state.pos[b1],state,goal)

def status(b1,state,goal):
    if is_done(b1,state,goal):
        return 'done'
    elif not state.clear[b1]:
        return 'inaccessible'
    elif not (b1 in goal.pos) or goal.pos[b1] == 'table':
        return 'move-to-table'
    elif is_done(goal.pos[b1],state,goal) and state.clear[goal.pos[b1]]:
        return 'move-to-block'
    else:
        return 'waiting'

def all_blocks(state):
    return state.clear.keys()


"""
In each pyhop2 planning method, the first argument is the current state (this is analogous to Python methods, in which the first argument is the class instance). The rest of the arguments must match the arguments of the task that the method is for. For example, ('pickup', b1) has a method holding_m(state,b1), as shown below.
"""

### methods for "move_blocks"

# def m_moveb(state,goal):
#     """
#     This method implements the following block-stacking algorithm:
#     If there's a block that can be moved to its final position, then
#     do so and call move_blocks recursively. Otherwise, if there's a
#     block that needs to be moved and can be moved to the table, then 
#     do so and call move_blocks recursively. Otherwise, no blocks need
#     to be moved.
#     """
#     for b1 in all_blocks(state):
#         s = status(b1,state,goal)
#         if s == 'move-to-table':
#             return [('pos',b1,'table'),goal]
#         elif s == 'move-to-block':
#             b2 = goal.pos[b1]
#             return [('pos',b1,b2),goal]
#         else:
#             continue
#     #
#     # if we get here, no blocks can be moved to their final locations
#     for b1 in all_blocks(state):
#         if status(b1,state,goal) == 'waiting':
#             return [('pos',b1,'table'),goal]
#     #
#     # if we get here, there are no blocks that need moving
#     return []

"""
Below, we tell pyhop2 that a Multigoal has only one method, m_moveb.
"""
pyhop2.declare_multigoal_methods(pyhop2.m_split_goals)

### methods for 'pos' goals

def m_move1(state,b1,b2):
    """
    If goal is ('pos',b1,b2) and we're holding nothing,
    then assert goals to get b1 and put it on b2.
    """
    if  b2 != 'hand' and not state.holding['hand']:
        if b2 == 'table':
            return [('clear',b1,True), ('pos', b1, 'hand'), ('pos', b1, b2)]
        else:
            return [('clear',b2,True), ('clear',b1,True), ('pos', b1, 'hand'), ('pos', b1, b2)]

def m_make_clear(state,b2,truth):
    if truth == True:
        if b2 == 'table' or state.clear[b2]:
            return []
        else:
            above_b2 = [b1 for b1 in state.pos if state.pos[b1] == b2]
            b1 = above_b2[0]                # the block that's on b2
            return [('clear',b1,True), ('pos',b1,'table')]
        

def m_hold(state,b1,hand):
    """
    If goal is ('pos',b1,'hand') and b1 is clear and we're holding nothing
    Generate either a pickup or an unstack subtask for b1.
    """
    if hand == 'hand' and state.clear[b1] and state.holding[hand] == False:
        if state.pos[b1] == 'table':
                return [('pickup',b1)]
        else:
                return [('unstack',b1,state.pos[b1])]
    else:
        return False

def m_put(state,b1,b2):
    """
    If goal is ('pos',b1,b2) and we're holding b1,
    Generate either a putdown or a stack subtask for b1.
    b2 is b1's destination: either the table or another block.
    """
    if b2 != 'hand' and state.pos[b1] == 'hand':
        if b2 == 'table':
                return [('putdown',b1)]
        elif state.clear[b2]:
                return [('stack',b1,b2)]
    else:
        return False

pyhop2.declare_goal_methods('pos',m_move1,m_hold,m_put)
pyhop2.declare_goal_methods('clear',m_make_clear)
