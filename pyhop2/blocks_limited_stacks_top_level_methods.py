import pyhop2
import blocks_limited_stacks_methods as meth
import blocks_limited_stacks_actions as act
import blocks_generator as gen

"""
This file contains methods used to solve entire problems,
complete single goals, and helper task methods
"""

"""
NOTE: The methods are only intended to solve complete plans,
so I'm not sure if trying to plan for a goal in which not all 
blocks from the initial state have a declared position will work.
"""

dummy_block = 'DUMMY_BLOCK'

def m_pos(state, b1, b2):
    """
    This method achieves the goal state.pos[b1] == b2.
    To do this, it clears b1, clears b2, (clears b1 again
    in case it somehow got covered while b2 was being cleared)
    and finally moves b1 to b2.
    If b2 is the table:
        if there is space on the table, it clears b1 and moves
        it to the table
        if there is no space on the table, it clears the shortest
        stack from the table whose bottom block does not belong on
        the table, then use that spot to place b1.
    """
    if state.pos[b1] == b2: return []

    if b2 != 'table':
        return [('make_clear', b1, b2), ('make_clear', b2, b1), ('make_clear', b1, b2),
                ('move_one', b1, b2)]
    else:
        empty_stack = None
        for i in range(len(state.stacks)):
            if state.stacks[i] == []:
                empty_stack = i
                break
        if empty_stack:
            state.stacks[empty_stack] += [dummy_block]
            return [('make_clear', b1, dummy_block), ('remove_dummy',), ('move_to_stack', b1, empty_stack)]
        else:
            state.stacks[0].insert(0,dummy_block)
            return [('clear', dummy_block, True), ('remove_dummy',), ('move_to_stack', b1, 0)]


pyhop2.declare_task_methods('pos', m_pos)


"""
This does not accomplish the goal state.clear[b1] == False
"""
# def m_clear(state, b1):
#     """Achieves the goal state.clear"""
#     return [('make_clear', b1, b1)]

# pyhop2.declare_goal_methods('clear', m_clear)

def m_multi_stack(state, goal):
    """
    This multigoal methods solves a goal by choosing a
    stack in the goal and building that stack in the state,
    builing each goal stack untill all goal stacks are built.
    """
    todo = []
    for i in range(len(state.stacks)):
        todo += m_multi_stack_aux(state, goal, i)
    return todo

def m_multi_stack_aux(state, goal, stack: int):
    """
    This helps the multigoal method by building a specific stack
    which is present in the goal.
    """
    list_goal = gen.gen_list_representation(goal, state.max_stacks)
    if len(state.stacks) > len(list_goal): return None
    to_do = []
    for stack in list_goal:
        for block in stack:
            if goal.pos[block] == 'table':
                to_do += [('dissolve_smallest_incorrect_stack', goal)]
            to_do += [('pos', block, goal.pos[block])]
    #to_do += [goal]
    return to_do


def m_dissolve_smallest_incorrect_stack(state, goal):
    """
    This identifies the smallest stack whose bottom
    block does not belong on the table acording to
    the goal. It then clears that stack from the table.
    """
    min_stack = None
    for i in range(len(state.stacks)):
        if state.stacks[i] == []:
            return []
        bottom = state.stacks[i][0]
        if goal.pos[bottom] != 'table': 
            if not min_stack: min_stack = i
            if len(state.stacks[i]) < len(state.stacks[min_stack]):
                min_stack = i
    if not min_stack: return None
    return [('dissolve_stack', min_stack)]

pyhop2.declare_task_methods('dissolve_smallest_incorrect_stack', m_dissolve_smallest_incorrect_stack)

def m_multi_level(state, goal):
    """
    This multigoal method works by completing each 'level' in the goal.
    blocks on level 0 are on the table,
    blocks on level 1 are on level 0 blocks,
    level 2 blocks are on level 1 blocks, etc.
    This method first accomplishes everything on level 0,
    then level 1, ... onto the highest level in the goal.
    """
    to_do = []
    curr_level = 0
    list_goal = gen.gen_list_representation(goal, state.max_stacks)
    ceiling = max(list(map(len, list_goal)))
    for i in range(ceiling):
        for stack in list_goal:
            if len(stack) > i:
                to_do += [('pos', stack[i], stack[i-1] if i != 0 else 'table')]
    return to_do

pyhop2.declare_task_methods('solve_goal', m_multi_level, m_multi_stack)
