"""
An expanded version of the "travel from home to the park" example in
my lectures.
Author: Dana Nau <nau@umd.edu>
Feb 18, 2021
"""

import pyhop2
import random


# For a more clever way to specify the domain name,
# see blocks_tasks.py or blocks_goals.py
domain_name = 'briefcaseworld'

# Create a new domain to contain the methods and operators
_current_domain = pyhop2.Domain(domain_name)


################################################################################
# states and rigid relations

rigid = pyhop2.State('rigid relations')
# These types are used by the 'is_a' helper function, later in this file
rigid.types = {
    'location': ['l1', 'l2', 'l3'],
    'object': ['o1', 'o2']}
#rigid.dist = { ('l1','l2'):1, ('l1','l3'):1, ('l2','l3'):1 }

# prototypical initial state
state0 = pyhop2.State()
state0.loc = {'o1': 'l2', 'o2': 'l3', 'briefcase': 'l1'}

###############################################################################
# Helper functions:

def is_a(variable,type):
    """
    In most classical planners, one would declare data-types for the parameters
    of each action, and the data-type checks would be done by the planner.
    Pyhop 2 doesn't have a way to do that, so the 'is_a' function gives us a
    way to do it in the preconditions of each action, command, and method.
    
    'is_a' doesn't implement subtypes (e.g., if rigid.type[x] = y and
    rigid.type[x] = z, it doesn't infer that rigid.type[x] = z. It wouldn't be
    hard to implement this, but it isn't needed in the simple-travel domain.
    """
    return variable in rigid.types[type]


###############################################################################
# Actions:

def move(state,l1,l2):
    if is_a(l1,'location') and is_a(l2,'location') and l1 != l2:
        if state.loc['briefcase'] == l1:
            state.loc['briefcase'] = l2
            return state

def take_out(state,x,l):
    if is_a(x,'object') and is_a(l,'location'):
        if state.loc[x] == 'briefcase' and state.loc['briefcase'] == l:
            state.loc[x] = l
            return state

def put_in(state,x,l):
    if is_a(x,'object') and is_a(l,'location'):
        if state.loc[x] == l and state.loc['briefcase'] == l:
            state.loc[x] = 'briefcase'
            return state

pyhop2.declare_actions(move, take_out, put_in)

###############################################################################
# Methods:

def organize(state, g):
    x = state.loc['briefcase']
    todo = []
    for obj in rigid.types['object']:
        if state.loc[obj] == 'briefcase' and g.loc[obj] == x:
            todo.append(('take_out', obj, x))
        elif state.loc[obj] == x and g.loc[obj] != x:
            todo.append(('put_in', obj, x))
    return todo

pyhop2.declare_task_methods('organize',organize)

def do_nothing(state, g):
    for obj in rigid.types['object']:
        if g.loc[obj] != state.loc[obj]:
            return None
    return []

def move_to_x(x):
    def move_to_(state, g):
        if state.loc['briefcase'] != x:
            return [('move', state.loc['briefcase'], x), ('move_briefcases', g)]
    move_to_.__name__ += x
    return move_to_

methods = [do_nothing] + [move_to_x(x) for x in rigid.types['location']]
pyhop2.declare_task_methods('switch_rooms',*methods)

def move_briefcases(state, g):
    return [('organize', g), ('switch_rooms', g)]

pyhop2.declare_task_methods('move_briefcases',move_briefcases)


###############################################################################
# Heuristic

def h(state, todo_list):
    goal = None
    for task in todo_list:
        if task[0] in _current_domain._task_method_dict:
            goal = task[1]
            break
    if goal:
        unsolved_rooms = {}
        for l in rigid.types['location']:
            unsolved_rooms[l] = 0
        for obj in rigid.types['object']:
            sloc = state.loc[obj]
            gloc = goal.loc[obj]
            if sloc == 'briefcase':
                unsolved_rooms[gloc] = 1
            elif sloc != gloc:
                unsolved_rooms[sloc] = 1
                unsolved_rooms[gloc] = 1
        unsolved = 0
        for l in unsolved_rooms:
            unsolved += unsolved_rooms[l]
        return unsolved
    return 0

###############################################################################
# Running the examples

print('-----------------------------------------------------------------------')
print(f"Created the domain '{domain_name}'. To run the examples, type this:")
print(f"{domain_name}.main()")

def main():
    # Code for use in paging and debugging
    from check_result import check_result, pause, set_trace
    
    # If we've changed to some other domain, this will change us back.
    pyhop2.set_current_domain(domain_name)
    pyhop2.print_domain()

    state1 = state0.copy()

    state1.display(heading='\nInitial state is')

    goal = pyhop2.State()
    goal.loc = {'o1': 'l1', 'o2': 'l2'}

    goal.display(heading='\nGoal is')

    pause()

    print("-- If verbose=3, the planner will print even more information.\n")
    result = pyhop2.find_plan_GBFS(state1,[('move_briefcases',goal)],h,verbose=3)