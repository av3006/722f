"""
The simple_travel_example.py file that was distributed with Pyhop 1,
with minor changes (see below) to make it compatible with Pyhop 2. 
Author: Dana Nau <nau@umd.edu>
Feb 18, 2021

Here are the differences between this file and the original Pyhop version:
- declare_actions instead of declare_operators
- print_actions instead of print_operators
- declare_task_methods instead of declare_methods
- pyhop2.find_plan instead of pyhop.pyhop
- pyhop2 instead of the other occurrences of pyhop
"""

import pyhop2


def taxi_rate(dist):
    return (1.5 + 0.5 * dist)

def walk(state,a,x,y):
    if state.loc[a] == x:
        state.loc[a] = y
        return state
    else: return False

def call_taxi(state,a,x):
    state.loc['taxi'] = x
    return state
    
def ride_taxi(state,a,x,y):
    if state.loc['taxi']==x and state.loc[a]==x:
        state.loc['taxi'] = y
        state.loc[a] = y
        state.owe[a] = taxi_rate(state.dist[x][y])
        return state
    else: return False

def pay_driver(state,a):
    if state.cash[a] >= state.owe[a]:
        state.cash[a] = state.cash[a] - state.owe[a]
        state.owe[a] = 0
        return state
    else: return False

pyhop2.declare_actions(walk, call_taxi, ride_taxi, pay_driver)
print('')
pyhop2.print_actions()



def travel_by_foot(state,a,x,y):
    if state.dist[x][y] <= 2:
        return [('walk',a,x,y)]
    return False

def travel_by_taxi(state,a,x,y):
    if state.cash[a] >= taxi_rate(state.dist[x][y]):
        return [('call_taxi',a,x), ('ride_taxi',a,x,y), ('pay_driver',a)]
    return False

pyhop2.declare_task_methods('travel',travel_by_foot,travel_by_taxi)
print('')
pyhop2.print_methods()

state1 = pyhop2.State('state1')
state1.loc = {'me':'home'}
state1.cash = {'me':20}
state1.owe = {'me':0}
state1.dist = {'home':{'park':8}, 'park':{'home':8}}

print("""
********************************************************************************
Call pyhop2.find_plan(state1,[('travel','me','home','park')]) with different verbosity levels
********************************************************************************
""")

print("- If verbose=0 (the default), pyhop2 returns the solution but prints nothing.\n")
pyhop2.find_plan(state1,[('travel','me','home','park')])

print('- If verbose=1, pyhop2 prints the problem and solution, and returns the solution:')
pyhop2.find_plan(state1,[('travel','me','home','park')],verbose=1)

print('- If verbose=2, pyhop2 also prints a note at each recursive call:')
pyhop2.find_plan(state1,[('travel','me','home','park')],verbose=2)

print('- If verbose=3, pyhop2 also prints the intermediate states:')
pyhop2.find_plan(state1,[('travel','me','home','park')],verbose=3)

