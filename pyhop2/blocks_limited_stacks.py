import pyhop2

pyhop2.Domain('blocks_limited_stacks')
import blocks_limited_stacks_actions as act
import blocks_limited_stacks_methods
import blocks_limited_stacks_goal_methods
import blocks_generator as gen
import blocks_limited_stacks_top_level_methods

"""
Helper methods
"""
def _apply_plan(s0, plan):
    s = s0
    for task in plan:
        action = pyhop2._current_domain._action_dict[task[0]]
        s = action(s.copy(), *task[1:])
    return s

def simple_state():
    s0 = pyhop2.State('s0')
    s0.pos = {'a': 'table', 'b': 'table', 'c': 'a', 'd': 'table', 
    'e': 'c', 'f': 'e', 'g': 'f', 'h': 'table'}
    s0.clear = {'a': False, 'b': True, 'c': False, 'd': True, 'e': False,
    'f': False, 'g': True, 'h': True}
    s0.stacks = [['a','c','e','f','g'], ['b'], ['d'], ['h'], [], []]
    s0.max_stacks = 6
    return s0

def small_state():
    s0 = pyhop2.State()
    s0.pos = {'0': '1', '1': '2', '2': 'table'}
    s0.stacks = [['2','1','0'],[],[],[],[],[]]
    s0.clear = {'0': True, '1': False, '2': False}
    s0.max_stacks = 6
    return s0

def small_goal():
    s = pyhop2.State()
    s.pos = {'2': '1', '1': '0', '0': 'table'}
    s.clear = {'2': True, '1': False, '0': False}
    s.stacks = [['0', '1', '2'], [], [], [], [], []]
    return s


"""state/goal generation parameters"""
num_blocks = 5
stack_prob = .5
max_stacks = 6

"""random initial state and goal"""
s_rand = gen.gen_blocks_state(num_blocks, stack_prob, max_stacks, start_state=True)
g_rand = gen.gen_blocks_state(num_blocks, stack_prob, max_stacks)

"""creating multigoal from random goal state"""
g = pyhop2.Multigoal()
g.pos = g_rand.pos

""" 
NOTE 1: Do no add the 'clear' dict to the goal;
The methods are not set up to solve state.clear[b1] == False
the 'clear' dict can be inferred from the 'pos' dict.
"""
# g.clear = g_rand.clear

"""
NOTE 2: The methods are only intended to solve complete plans,
so I'm not sure if trying to plan for a goal in which not all 
blocks from the initial state have a declared position will work.
"""

"""Finding a solution, the displaying the initial state and goal"""

"""
You can either pass a [multigoal] as the todo
or you can pass [('solve_goal', s0, goal_state)] as the todo
"""
print(pyhop2.find_plan(s_rand, [g]))
print(pyhop2.find_plan(s_rand, [('solve_goal', g_rand)]))
print(gen.gen_list_representation(s_rand, max_stacks))
print(gen.gen_list_representation(g, max_stacks))


"""Some simple tests I used for debugging"""
# s0 = simple_state()
# print(act.get_block_above(s_small, '1'))
# print(pyhop2.find_plan(s0, [('make_clear_distribute', 'a', 'd')]))
# print(pyhop2.find_plan(s0, [('make_clear_dump_to_smallest', 'a', 'd')]))
# print(pyhop2.find_plan(s0, [('make_clear_split_to_nbr', 'a', 'c')]))
# print(pyhop2.find_plan(s0, [('make_clear_split_to_smallest', 'a', 'b')]))
# print(pyhop2.find_plan(s0, [('make_clear_split_to_nbr', 'a', 'd')]))
# print(pyhop2.find_plan(s0, [('pos', 'a', 'd')]))
# print(pyhop2.find_plan(s0, [('pos', 'a', 'c')]))
# print(pyhop2.find_plan(s_small, [('pos', '0', 'table'), ('pos', '1', '0')]))
# print(pyhop2.find_plan(s_small, [('pos', '0', 'table')]))
# plan =pyhop2.find_plan(s_small, [('pos', '0', 'table')])
# state = _apply_plan(s_small, plan)
# print(state.stacks)
# print(pyhop2.find_plan(state, [('pos', '2', '0')]))