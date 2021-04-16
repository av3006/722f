import pyhop2
import random
from timeit import default_timer as timer

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
    'location': [],
    'object': []}
#rigid.dist = { ('l1','l2'):1, ('l1','l3'):1, ('l2','l3'):1 }

###############################################################################
# Helper functions:

def is_a(variable,type):
    return variable in rigid.types[type]

def locations():
    return rigid.types['location']

def objects():
    return rigid.types['object']


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
    for obj in objects():
        if state.loc[obj] == 'briefcase' and g.loc[obj] == x:
            todo.append(('take_out', obj, x))
        elif state.loc[obj] == x and g.loc[obj] != x:
            todo.append(('put_in', obj, x))
    return todo

pyhop2.declare_task_methods('organize',organize)

def do_nothing(state, g):
    for obj in objects():
        if g.loc[obj] != state.loc[obj]:
            return None
    return []

def move_to_x(x):
    def move_to_(state, g):
        if state.loc['briefcase'] != x:
            return [('move', state.loc['briefcase'], x), ('move_briefcases', g)]
    move_to_.__name__ += x
    return move_to_

# move methods declared in initialize function

def move_briefcases(state, g):
    return [('organize', g), ('switch_rooms', g)]

pyhop2.declare_task_methods('move_briefcases',move_briefcases)


###############################################################################
# Cost
# Define a function that maps 

###############################################################################
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
        for l in locations():
            unsolved_rooms[l] = 0
        for obj in objects():
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

def initialize_random_domain(n):
    rigid.types['location'] = ['l' + str(i) for i in range(n)]
    rigid.types['object'] = ['o' + str(i) for i in range(n)]
    
    methods = [do_nothing] + [move_to_x(x) for x in locations()]
    pyhop2.declare_task_methods('switch_rooms',*methods)
    
    state0 = pyhop2.State()
    state0.loc = {}
    goal = pyhop2.State()
    goal.loc = {}
    for o in objects():
        state0.loc[o] = random.sample(locations(), 1)[0]
        goal.loc[o] = random.sample(locations(), 1)[0]
    state0.loc['briefcase'] = random.sample(locations(), 1)[0]

    return state0, goal

def main():
    # Code for use in paging and debugging
    from check_result import check_result, pause, set_trace
    
    # If we've changed to some other domain, this will change us back.
    pyhop2.set_current_domain(domain_name)
    pyhop2.print_domain()


    # state0.display(heading='\nInitial state is')
    # goal.display(heading='\nGoal is')

    print('\nBeginning testing\n')
    print('Result length\tTime')
    state0, goal = initialize_random_domain(10)

    
    start = timer()
    result = pyhop2.find_plan_GBFS(state0,[('move_briefcases',goal)],h,verbose=0)
    end = timer() 
    print(f'{len(result)}\t\t{end - start}')

    start = timer()
    result = pyhop2.find_plan_GBFS(state0,[('move_briefcases',goal)],h,a_star=True,verbose=0)
    end = timer() 
    print(f'{len(result)}\t\t{end - start}')