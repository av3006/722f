import pyhop2
import random
from itertools import combinations
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
rigid.dist = {}

###############################################################################
# Helper functions:

def is_a(variable,type):
    return variable in rigid.types[type]

def locations():
    return rigid.types['location']

def objects():
    return rigid.types['object']

def distance(x,y):
    return rigid.dist.get((x,y)) or rigid.dist.get((y,x))

def unsolved_locations(state, goal, to_move=False):
    unsolved_loc = set()
    for obj in objects():
        sloc = state.loc[obj]
        gloc = goal.loc[obj]
        if sloc == 'briefcase':
            unsolved_loc.add(gloc)
        elif sloc != gloc:
            unsolved_loc.add(sloc)
            if not to_move:
                unsolved_loc.add(gloc)
    return unsolved_loc

def locations_to_move(state, goal):
    return unsolved_locations(state, goal, to_move=True)


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
        if x in locations_to_move(state, g) and state.loc['briefcase'] != x:
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

def h_moves(state, todo_list):
    goal = None
    for task in todo_list:
        if task[0] in _current_domain._task_method_dict:
            goal = task[1]
            break
    if goal:
        unsolved_loc = unsolved_locations(state, goal)
        return len(unsolved_loc)
    return 0

def c_moves(action):
    return 1 if action[0] == 'move' else 0

def c_dist(action):
    return distance(*action[1:]) if action[0] == 'move' else 0


###############################################################################
# Running the examples

print('-----------------------------------------------------------------------')
print(f"Created the domain '{domain_name}'. To run the examples, type this:")
print(f"{domain_name}.main()")

def initialize_random_domain(n):
    rigid.types['location'] = ['l' + str(i) for i in range(n)]
    rigid.types['object'] = ['o' + str(i) for i in range(n)]
    for pair in combinations(locations(), r=2):
        rigid.dist[pair] = 1
    methods = [do_nothing] + [move_to_x(x) for x in locations()]
    pyhop2.declare_task_methods('switch_rooms',*methods)

def initialize_random_dist():
    for pair in rigid.dist:
        rigid.dist[pair] = random.randrange(1,6)

def create_random_problem():
    state0 = pyhop2.State()
    state0.loc = {}
    goal = pyhop2.State()
    goal.loc = {}
    for o in objects():
        state0.loc[o] = random.sample(locations(), 1)[0]
        goal.loc[o] = random.sample(locations(), 1)[0]
    state0.loc['briefcase'] = random.sample(locations(), 1)[0]
    return state0, goal

def cost(result, c):
    final = 0
    for action in result:
        final += c(action)
    return final

def test(h, c, size=10, iter=100):
    initialize_random_domain(size)
    costSum = {'base': 0, 'gbfs': 0, 'a_star': 0}
    timeSum = {'base': 0, 'gbfs': 0, 'a_star': 0}
    for i in range(iter):
        print(i)
        initialize_random_dist()
        state0, goal = create_random_problem()

        start = timer()
        result = pyhop2.find_plan(state0,[('move_briefcases',goal)],verbose=0)
        end = timer() 
        costSum['base'] += cost(result, c)
        timeSum['base'] += end - start

        for (a_star, name) in [(True, 'a_star'), (False, 'gbfs')]:
            start = timer()
            result = pyhop2.find_plan_GBFS(state0,[('move_briefcases',goal)],h,a_star=a_star,c=c, verbose=0)
            end = timer() 
            costSum[name] += cost(result, c)
            timeSum[name] += end - start

    for metric in [costSum, timeSum]:
        for name in metric:
            metric[name] /= float(iter)

    return costSum, timeSum

def main():
    # Code for use in paging and debugging
    from check_result import check_result, pause, set_trace
    
    # If we've changed to some other domain, this will change us back.
    pyhop2.set_current_domain(domain_name)
    # pyhop2.print_domain()


    # state0.display(heading='\nInitial state is')
    # goal.display(heading='\nGoal is')

    avgCost, avgTime = test(h_moves, c_dist, size=15, iter=500)
    print(avgCost, avgTime)