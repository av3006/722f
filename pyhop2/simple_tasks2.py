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
domain_name = 'simple_tasks2'

# Create a new domain to contain the methods and operators.
pyhop2.Domain(domain_name)


################################################################################
# states and rigid relations

rigid = pyhop2.State('rigid relations')
# These types are used by the 'is_a' helper function, later in this file
rigid.types = {
    'person':   ['alice', 'bob'],
    'location': ['home_a', 'home_b', 'park', 'station'],
    'taxi':     ['taxi1', 'taxi2']}
rigid.dist = {
    ('home_a', 'park'):8,    ('home_b', 'park'):2, 
    ('station', 'home_a'):1, ('station', 'home_b'):7,
    ('home_a', 'home_b'):7,  ('station','park'):9}

# First initial state. In this one, both taxis are in good condition
state0a = pyhop2.State('state0a')
state0a.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'park',
    'taxi2':'station'}
state0a.cash = {'alice':20, 'bob':15}
state0a.owe = {'alice':0, 'bob':0}
state0a.taxi_condition = {'taxi1':'good', 'taxi2':'good'}


# Second initial state. In this one, both taxis are in bad condition
state0b = pyhop2.State('state0b')
state0b.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'park',
    'taxi2':'station'}
state0b.cash = {'alice':20, 'bob':15}
state0b.owe = {'alice':0, 'bob':0}
state0b.taxi_condition = {'taxi1':'bad', 'taxi2':'bad'}



###############################################################################
# Helper functions:


def taxi_rate(dist):
    "In this domain, the taxi fares are quite low :-)"
    return (1.5 + 0.5 * dist)


def distance(x,y):
    """
    If rigid.dist[(x,y)] = d, this function figures out that d is both
    the distance from x to y and the distance from y to x.
    """
    return rigid.dist.get((x,y)) or rigid.dist.get((y,x))


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

def walk(state,p,x,y):
    if is_a(p,'person') and is_a(x,'location') and is_a(y,'location') and x != y:
        if state.loc[p] == x:
            state.loc[p] = y
            return state

def call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        state.loc['taxi1'] = x
        state.loc[p] = 'taxi1'
        return state
    
def ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            state.loc[taxi] = y
            state.owe[p] = taxi_rate(distance(x,y))
            return state

def pay_driver(state,p,y):
    if is_a(p,'person'):
        if state.cash[p] >= state.owe[p]:
            state.cash[p] = state.cash[p] - state.owe[p]
            state.owe[p] = 0
            state.loc[p] = y
            return state


pyhop2.declare_actions(walk, call_taxi, ride_taxi, pay_driver)


###############################################################################
# Commands:


# this does the same thing as the action model
def c_walk(state,p,x,y):
    if is_a(p,'person') and is_a(x,'location') and is_a(y,'location'):
        if state.loc[p] == x:
            state.loc[p] = y
            return state


# c_call_taxi, version used in simple_tasks2
# like the action model, but chooses the taxi randomly
def c_call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        taxi = 'taxi{}'.format(1+random.randrange(2))
        print(f'Action> The taxi is chosen randomly.')
        print(f'Action> This time it is {taxi}.')
        state.loc[taxi] = x
        state.loc[p] = taxi
        return state


# c_ride_taxi, version used in simple_tasks2.
# If the taxi isn't in good condition, it will break down.
def c_ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            if state.taxi_condition[taxi] == 'good':
                state.loc[taxi] = y
                state.owe[p] = taxi_rate(distance(x,y))
                return state
            else:
                print('Action> c_ride_taxi failed.')


# this does the same thing as the action model
def c_pay_driver(state,p,y):
    return pay_driver(state,p,y)


pyhop2.declare_commands(c_walk, c_call_taxi, c_ride_taxi, c_pay_driver)

###############################################################################
# Methods:

def do_nothing(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x == y:
            return []

def travel_by_foot(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x != y and distance(x,y) <= 2:
            return [('walk',p,x,y)]

def travel_by_taxi(state,p,y):
    if is_a(p,'person') and is_a(y,'location'):
        x = state.loc[p]
        if x != y and state.cash[p] >= taxi_rate(distance(x,y)):
            return [('call_taxi',p,x), ('ride_taxi',p,y), ('pay_driver',p,y)]

pyhop2.declare_task_methods('travel',do_nothing,travel_by_foot,travel_by_taxi)


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

    state0a.display(heading='\nInitial state')

    pause()
    print("Use run_lazy_lookahead to get Alice to the park.\n")
    pyhop2.run_lazy_lookahead(state0a,[('travel','alice','park')],verbose=1)
    print('')
    pause()

    print("""
Next is a demonstration of what can happen if your HTN methods are too brittle.
We'll try to use run_lazy_lookahead to get Alice to the park, but the taxi will
break down while Alice is in it.  run_lazy_lookahead will call find_plan again,
but find_plan will fail because the HTN methods don't handle this case.
    """)


    state0b.display(heading='The initial state is')

    print('Next, the call to run_lazy_lookahead ...')
    pause()

    pyhop2.run_lazy_lookahead(state0b,[('travel','alice','park')],verbose=1)
    pause()

    print("No more examples")


###############################################################################
# At this point, I used to call main() so the examples would run automatically,
# but I've removed that to maintain uniformity with the other example domains.
