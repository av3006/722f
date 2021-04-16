import pyhop2
from pyhop2 import _current_domain
import blocks_limited_stacks_actions as act
import blocks_generator as gen

#################################################
#Helper functions
#################################################
max_stacks = 5
_current_domain.max_stacks = max_stacks

def set_max_stacks(n):
    global max_stacks
    max_stacks = n
    pyhop2.Domain()
    _current_domain.max_stacks = n
    pyhop2.declare_task_methods('move_one', m_move_one)
    pyhop2.declare_task_methods('move_somewhere_else', *[move_to_stack_x(x) for x in range(_current_domain.max_stacks)])
    pyhop2.declare_task_methods('clear_block', m_clear_block)
    pyhop2.declare_task_methods('clear_some_stack', *[clear_stack_x(x) for x in range(_current_domain.max_stacks)])
    pyhop2.declare_task_methods('clear_stack', m_clear_stack)
    pyhop2.declare_task_methods('pos', m_pos)

def first_clear_stack(state):
    for i in range(len(state.stacks)):
        if not state.stacks[i]:
            return i

def is_level_done(state, goal, level):
    list_goal = gen.gen_list_representation(goal, _current_domain.max_stacks)
    for stack in list_goal:
        if len(stack) > level:
            curr_block = stack[level]
            if state.pos[curr_block] != goal.pos[curr_block]:
                return False
    return True


#################################################
#actions
#################################################
def m_put_on_stack(state, b1, stack):
    if not state.stacks[stack]:
        return [('move_one', b1, 'table')]
    else:
        top = state.stacks[stack][-1]
        return [('move_one', b1, top)]

pyhop2.declare_task_methods('put_on_stack', m_put_on_stack)

#################################################
#methods
#################################################

def m_move_one(state, b1, b2):
    """
    moves one block to location b2 regardless of
    whether this requires stack, unstack, or restack
    """
    if state.pos[b1] == 'table':
        return [('stack', b1, b2)]
    elif b2 == 'table':
        return [('unstack', b1, state.pos[b1])]
    else:
        return [('restack', b1, state.pos[b1], b2)]

pyhop2.declare_task_methods('move_one', m_move_one)

def move_to_stack_x(x):
    def m_move_to_stack_(state, b1):
        if act.get_stack_of_block(state, b1) != x:
            return [('put_on_stack', b1, x)]
    m_move_to_stack_.__name__ += str(x)
    return m_move_to_stack_

pyhop2.declare_task_methods('move_somewhere_else', *[move_to_stack_x(x) for x in range(_current_domain.max_stacks)])

for stack in range(_current_domain.max_stacks):
    pyhop2.declare_task_methods(f'move_somewhere_else_except_stack_{stack}', \
        *[move_to_stack_x(x) for x in range(_current_domain.max_stacks) if x != stack])


def clear_stack_x(x):
    def m_clear_stack_(state):
        return [('clear_stack', x)]
    m_clear_stack_.__name__ += str(x)
    return m_clear_stack_

pyhop2.declare_task_methods('clear_some_stack', *[clear_stack_x(x) for x in range(_current_domain.max_stacks)])

def m_clear_block(state, b1):
    if state.clear[b1]:
        return []
    else:
        b_above = act.get_block_above(state, b1)
        return [('clear_block', b_above), ('move_somewhere_else', b_above)]

def m_clear_2_blocks(state, b1, b2):
    if state.clear[b1]:
        if state.clear[b2]:
            return []
        else:
            b_above = act.get_block_above(state, b2)
            stack = act.get_stack_of_block(state, b1)
            return [('clear_2_blocks', b1 , b_above), (f'move_somewhere_else_except_stack_{stack}', b_above)]
    else:
        b_above = act.get_block_above(state, b1)
        stack = act.get_stack_of_block(state, b2)
        return [('clear_2_blocks', b_above ,b2), (f'move_somewhere_else_except_stack_{stack}', b_above)]

def m_clear_block_avoiding_stack(state, b1, stack):
    if state.clear[b1]:
        return []
    else:
        b_above = act.get_block_above(state, b1)
        return([('clear_block_avoiding_stack', b_above, stack), \
            (f'move_somewhere_else_except_stack_{stack}', b_above)])


pyhop2.declare_task_methods('clear_block', m_clear_block)
pyhop2.declare_task_methods('clear_2_blocks', m_clear_2_blocks)
pyhop2.declare_task_methods('clear_block_avoiding_stack', m_clear_block_avoiding_stack)

def m_clear_stack(state, stack):
    if not state.stacks[stack]:
        return []
    else:
        bottom = state.stacks[stack][0]
        return [('clear_block', bottom), ('move_somewhere_else', bottom)]

def m_clear_stack_avoiding_stack(state, stack1, stack2):
    if not state.stacks[stack1]:
        return []
    else:
        bottom = state.stacks[stack1][0]
        return [('clear_block_avoiding_stack', bottom, stack2), (f'move_somewhere_else_except_stack_{stack2}', bottom)]

def m_clear_some_incorrect_stack(state, goal):
    for i in range(len(state.stacks)):
        if not state.stacks[i]:
            return []
        else:
            bottom = state.stacks[i][0]
            if goal.pos[bottom] != 'table':
                return [('clear_stack', i)]

pyhop2.declare_task_methods('clear_stack', m_clear_stack)
pyhop2.declare_task_methods('clear_stack_avoiding_stack', m_clear_stack_avoiding_stack)
pyhop2.declare_task_methods('clear_some_incorrect_stack', m_clear_some_incorrect_stack)

def m_pos(state, b1, b2):
    sub = []
    if state.pos[b1] == b2:
        return []
    sub += [('clear_block', b1)]
    if b2 == 'table' and not first_clear_stack(state):
        sub += [('clear_some_stack',)]
    if b2 != 'table':
        sub += [('clear_block', b2)]
    sub += [('move_one', b1 ,b2)]
    return sub

def m_pos_efficient(state, b1 ,b2, goal):
    if state.pos[b1] == b2:
        return []
    elif b2 != 'table':
        return [('clear_block_avoiding_stack', b1, act.get_stack_of_block(state, b2)), \
            ('clear_block_avoiding_stack', b2, act.get_stack_of_block(state, b1)), ('move_one', b1, b2)]
    else:
        clear_stack = first_clear_stack(state)
        if clear_stack != None:
            return[('clear_block_avoiding_stack', b1, clear_stack), ('move_one', b1 ,b2)]
        else:
            return[('clear_some_incorrect_stack', goal), ('pos_efficient', b1 ,b2, goal)]

pyhop2.declare_task_methods('pos', m_pos_efficient)
pyhop2.declare_task_methods('pos_efficient', m_pos_efficient)


#################################################
#Top level methods
#################################################

def m_multi_level(state, goal):
    return [('multi_level_aux', goal, 0)]

def m_multi_level_aux(state, goal, curr_level):
    """
    This multigoal method works by completing each 'level' in the goal.
    blocks on level 0 are on the table,
    blocks on level 1 are on level 0 blocks,
    level 2 blocks are on level 1 blocks, etc.
    This method first accomplishes everything on level 0,
    then level 1, ... onto the highest level in the goal.
    """
    list_goal = gen.gen_list_representation(goal, _current_domain.max_stacks)
    ceiling = max(list(map(len, list_goal)))
    if curr_level > ceiling:
        return []
    elif is_level_done(state, goal, curr_level):
        return [('multi_level_aux', goal, curr_level + 1)]
    else:
        blocks_at_curr_level = []
        for stack in list_goal:
            if len(stack) > curr_level:
                blocks_at_curr_level += [stack[curr_level]]
        return [('pos', b1, goal.pos[b1], goal) for b1 in blocks_at_curr_level] + [('multi_level_aux', goal, curr_level)]

pyhop2.declare_task_methods('multi_level_aux', m_multi_level_aux)
pyhop2.declare_task_methods('solve_goal', m_multi_level)


######################################################################################
# Heuristic
######################################################################################3

def gen_weeak_h(goal):
    def h(state, todo):
        h_val = 0
        for block in goal.pos:
            if state.pos[block] != goal.pos[block]:
                h_val += 1
        return h_val
    return h

def gen_strong_h(goal):
    def h(state, todo):
        goal_stacks = gen.gen_list_representation(goal, max_stacks)
        h_val = sum(list(map(len, goal_stacks)))
        for stack in goal_stacks:
            for block in stack:
                if state.pos[block] == goal.pos[block]:
                    h_val -= 1
                else:
                    break
        return h_val
    return h


######################################################################################
#Debugging
#####################################################################################3

    

def simple_state():
    s0 = pyhop2.State('s0')
    s0.pos = {'a': 'table', 'b': 'table', 'c': 'a', 'd': 'table', 
    'e': 'c', 'f': 'e', 'g': 'table', 'h': 'table'}
    s0.clear = {'a': False, 'b': True, 'c': False, 'd': True, 'e': False,
    'f': True, 'g': True, 'h': True}
    s0.stacks = [['a','c','e','f'], ['b'], ['d'], ['h'], ['g']]
    s0.max_stacks = _current_domain.max_stacks
    return s0

def small_state():
    s0 = pyhop2.State()
    s0.pos = {'a': 'table', 'b': 'table', 'c': 'a', 'd': 'table', 'e': 'table', 'f': 'table'}
    s0.clear = {'a': False, 'b': True, 'c': True, 'd': True, 'e': True, 'f': True}
    s0.stacks = [['a','c'],['b'],['d'],['e'],['f']]
    s0.max_stacks = _current_domain.max_stacks
    return s0

def main():
    s0 = simple_state()
    g = s0.copy()
    g.pos['e'] = 'table'
    g.pos['f'] = 'e'
    g.pos['b'] = 'h'
    g.stacks[0] = ['a','c',]
    g.stacks[1] = ['f','e']
    g.stacks[3] = ['h','b']
    num_blocks = 7
    stacking_prob = .5

    s_rand = gen.gen_blocks_state(num_blocks, stacking_prob, max_stacks, True)
    g_rand = gen.gen_blocks_state(num_blocks, stacking_prob, max_stacks)

    print(gen.gen_list_representation(s0, _current_domain.max_stacks))
    print(gen.gen_list_representation(g, _current_domain.max_stacks))
    print(pyhop2.find_plan(s0, [('pos', 'e', 'table', g)], verbose=2))
    print(pyhop2.find_plan(s0, [('solve_goal', g)], verbose=3))
    print(pyhop2.find_plan_GBFS(s0, [('solve_goal', g)], gen_strong_h(g)))
    #print(pyhop2.find_plan(s_rand, [('solve_goal', g_rand)]))

#main()