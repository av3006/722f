"""
An expanded version of the "travel from home to the park" example in
my lectures, modified to use goals instead of tasks.
Author: Dana Nau <nau@umd.edu>
Feb 22, 2021
"""

import pyhop2
import random


# For a more clever way to specify the domain name,
# see blocks_tasks.py or blocks_goals.py
domain_name = 'simple_goals'

# Create a new domain to contain the methods and operators
pyhop2.Domain(domain_name)


################################################################################
# rigid relations, states, goals

rigid = pyhop2.State('rigid relations')
# These types are used by the 'is_a' helper function, later in this file
rigid.types = {'person':['alice', 'bob'],
    'location':['home_a', 'home_b', 'park', 'station', 'downtown'],
    'taxi':['taxi1', 'taxi2']}
rigid.dist = {('home_a', 'park'):8, ('home_b', 'park'):2, 
    ('station', 'home_a'):1, ('station', 'home_b'):7, ('downtown', 'home_a'):3,
    ('downtown', 'home_b'):7, ('station','downtown'):2}

# prototypical initial state
state0 = pyhop2.State()
state0.loc = {'alice':'home_a', 'bob':'home_b', 'taxi1':'downtown',
    'taxi2':'station'}
state0.cash = {'alice':20, 'bob':15}
state0.owe = {'alice':0}

# initial goal
goal1 = pyhop2.Multigoal('goal1')
goal1.loc = {'alice':'park'}

# another initial goal
goal2 = pyhop2.Multigoal('goal2')
goal2.loc = {'bob':'park'}

# bigger initial goal
goal3 = pyhop2.Multigoal('goal3')
goal3.loc = {'alice':'park', 'bob':'park'}


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


# c_call_taxi
# like the action model, but chooses the taxi randomly
def c_call_taxi(state,p,x):
    if is_a(p,'person') and is_a(x,'location'):
        taxi = 'taxi{}'.format(1+random.randrange(2))
        print(f'Action> the taxi is chosen randomly. This time it is {taxi}.')
        state.loc[taxi] = x
        state.loc[p] = taxi
        return state


# c_ride_taxi, version used in simple_tasks1
# this does the same thing as the action model
def c_ride_taxi(state,p,y):
    # if p is a person, p is in a taxi, and y is a location:
    if is_a(p,'person') and is_a(state.loc[p],'taxi') and is_a(y,'location'):
        taxi = state.loc[p]
        x = state.loc[taxi]
        if is_a(x,'location') and x != y:
            state.loc[taxi] = y
            state.owe[p] = taxi_rate(distance(x,y))
            return state


# this does the same thing as the action model
def c_pay_driver(state,p,y):
    return pay_driver(state,p,y)


pyhop2.declare_commands(c_walk, c_call_taxi, c_ride_taxi, c_pay_driver)

###############################################################################
# Methods:

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

pyhop2.declare_goal_methods('loc',travel_by_foot,travel_by_taxi)

# Pyhop 2 provides a built-in multigoal method called m_split_goals.
# Given a multigoal G, it separates G into a collection of individual goals.
# It returns a list of goals [g1, ..., gn, G], where g1, ..., gn are the
# goals in G that aren't true in the current state. This causes Pyhop 2 to
# achieve g1, ..., gn sequentially, and then to call m_split_goals again,
# to re-achieve any goals that (due to deleted-condition interactions)
# became false while accomplishing g1, ..., gn.
# The main problem with m_split_goals is that it isn't smart about choosing
# the order in which to achieve g1, ..., gn. In general, some orders will
# work better than others, and a possible project would be to create a
# heuristic function to choose a good order.

pyhop2.declare_multigoal_methods(pyhop2.m_split_goals)


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

#    state1.display(heading='\nThe initial state is')

    print("""
Next, several planning problems using the above domain and initial state.
""")
    pause()
    
    print("""
Below, we give find_plan the goal of having alice be at the park.
We do it several times with different values for 'verbose'.
""")


    expected = [('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park')]

    print("If verbose=0, the planner returns the solution but prints nothing:")
    result = pyhop2.find_plan(state1,[('loc','alice','park')],verbose=0)
    check_result(result,expected)

    print("""If verbose=1, then in addition to returning the solution, the planner prints
both the problem and the solution"
""")
    result = pyhop2.find_plan(state1,[('loc','alice','park')],verbose=1)
    check_result(result,expected)

    print("""If verbose=2, the planner also prints a note at each recursive call.  Below,
_verify_g is a task used by the planner to check whether a method has
achieved its goal.
""")
    result = pyhop2.find_plan(state1,[('loc','alice','park')],verbose=2)
    check_result(result,expected)
    pause()

    print("""
If verbose=3, the planner prints even more information. 
""")
    result = pyhop2.find_plan(state1,[('loc','alice','park')],verbose=3)
    check_result(result,expected)

    pause()
    print("""
Next, we give find_plan a sequence of two goals: first for Alice to be at the
park, then for Bob to be at the park. Since this is a sequence, it doesn't
matter whether they're both at the park at the same time.
""")

    plan = pyhop2.find_plan(state1,[('loc','alice','park'),('loc','bob','park')],verbose=2)

    check_result(plan,[('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park'), ('walk', 'bob', 'home_b', 'park')])

    pause()


    state1.display(heading='\nInitial state')

    print("""
A multigoal g looks similar to a state, but usually it includes just a few of
the state variables rather than all of them. It specifies *desired* values
for those state variables, rather than current values. The goal is to produce
a state that satisfies all of the desired values.

Below, goal3 is the goal of having Alice and Bob at the park at the same time.
""")
    
    goal3.display()
    
    
    print("""
Next, we'll call find_plan on goal3, with verbose=2. In the printout,
_verify_mg is a task used by the planner to check whether a multigoal
method has achieved all of the values specified in the multigoal.
""")
    pause()
    
    plan = pyhop2.find_plan(state1,[goal3],verbose=2)
    check_result(plan,[('call_taxi', 'alice', 'home_a'), ('ride_taxi', 'alice', 'park'), ('pay_driver', 'alice', 'park'), ('walk', 'bob', 'home_b', 'park')])

    pause()
    print('\nCall run_lazy_lookahead with verbose=1:\n')

    new_state = pyhop2.run_lazy_lookahead(state1,[('loc','alice','park')],verbose=1)
    print('')
    
    pause()
    
    print('\nAlice is now at the park, so the planner will return an empty plan:\n')

    plan = pyhop2.find_plan(new_state,[('loc','alice','park')],verbose=1)
    check_result(plan,[])

    print("No more examples")


###############################################################################
# At this point, I used to call main() so the examples would run automatically,
# but I've removed that to maintain uniformity with the other example domains.
