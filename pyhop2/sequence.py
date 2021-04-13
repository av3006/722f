"""
An expanded version of the "travel from home to the park" example in
my lectures.
Author: Dana Nau <nau@umd.edu>
Feb 18, 2021
"""

import pyhop2
import random
from timeit import default_timer as timer

# For a more clever way to specify the domain name,
# see blocks_tasks.py or blocks_goals.py
domain_name = 'sequence'

# Create a new domain to contain the methods and operators
_current_domain = pyhop2.Domain(domain_name)


################################################################################
# states and rigid relations

rigid = pyhop2.State('rigid relations')
# These types are used by the 'is_a' helper function, later in this file
rigid.types = {
    'character': ['START', 'a', 'b', 'c', 'aa', 'bb', 'END']}
rigid.perm = { 'START': [],
                'a': ['START'],
                'b': ['a'],
                'c': ['b', 'START'],
                'END': ['c', 'bb'],
                'aa': ['START'],
                'bb': ['aa'] }

# prototypical initial state
state0 = pyhop2.State()
state0.last_char = 'START'

###############################################################################
# Helper functions:

# returns if c1 -> c2 is a permissibility assertion
def permissible(c1, c2):
    return c1 in rigid.perm[c2]

# returns list of characters c' such that c' -> c is a permissibility assertion
def neighbors(c):
    return rigid.perm[c]

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

def append(state,x,y):
    if is_a(x,'character') and is_a(y,'character'):
        if state.last_char == x and permissible(x, y):
            state.last_char = y
            return state

pyhop2.declare_actions(append)

###############################################################################
# Methods:

def do_nothing(state,y):
    if is_a(y,'character') and state.last_char == y:
        return []

def ms(x):
    def make_string(state,y):
        if is_a(y,'character') and permissible(x,y):
            return [('make_string', x), ('append', x, y)]
    make_string.__name__ += '_' + x
    return make_string

methods = [do_nothing] + [ms(x) for x in rigid.types['character']]
pyhop2.declare_task_methods('make_string',*methods)


###############################################################################
# Heuristic

def BFS_dist(x,y):
    if x == y: return 0
    visited = {}
    for c in rigid.types['character']:
        visited[c] = False
    queue = [x]
    dist = 0
    while queue:
        x = queue.pop(0)
        dist += 1
        for n in neighbors(x):
            if n == y:
                return dist
            if not visited[n]:
                visited[n] = True
                queue.append(n)
    return float('inf')

BFS_dist_vals = {}
for c in rigid.types['character']:
    BFS_dist_vals[c] = BFS_dist(c, 'START')

def h_BFS(state, todo_list):
    if todo_list:
        task = todo_list[0]
        if task[0] == 'make_string':
            return BFS_dist_vals[task[1]]
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

    pause()

    print("-- If verbose=3, the planner will print even more information.\n")
    start1 = timer()
    result = pyhop2.find_plan_GBFS(state1,[('make_string','END')],h_BFS,verbose=3)
    end1 = timer()
    print(end1-start1)
    start2 = timer()
    result = pyhop2.find_plan_a_star(state1,[('make_string','END')],h_BFS,verbose=3)
    end2 = timer()
    print(end2-start2)

if __name__ == "__main__":
    main()