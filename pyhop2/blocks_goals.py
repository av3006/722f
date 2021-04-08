"""
Top-level file for blocks_goals.
Author: Dana Nau <nau@umd.edu>
Feb 18, 2021
"""

# For use in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import pyhop2

# Code for use in paging and debugging
from check_result import check_result, pause, set_trace


# First, create a new domain having the same name as the current file. To do
# this, I retrieve the value of __name__, which (while this file is being
# loaded) is the filename. Thus I can copy and paste this same code into other
# files without having to change a hard-coded domain name each time.
pyhop2.Domain(__name__)

# Next, import the actions and tasks files. I thought about making them
# into a package, but ultimately decided not to. When I tried it, it made
# several things more complicated than I wanted - things that I didn't want
# to try to explain to students who have never seen packages before.

exec(f"import {__name__}_actions")      # kludge
exec(f"import {__name__}_methods")      # kludge


#############     beginning of tests     ################

print('-----------------------------------------------------------------------')
print(f"Created the domain '{__name__}'. To run the examples, type this:")
print(f'{__name__}.main()')

def main():
    # If we've changed to some other domain, this will change us back.
    print(f"Changing current domain to {__name__}, if it isn't that already.")
    pyhop2.set_current_domain(__name__)

    pyhop2.print_domain()

    print("\nLet's call find_plan on some simple things that should fail.\n")

    state1 = pyhop2.State('state1')
    state1.pos={'a':'b', 'b':'table', 'c':'table'}
    state1.clear={'c':True, 'b':False,'a':True}
    state1.holding={'hand':False}

    state1.display('Initial state is')

    plan = pyhop2.find_plan(state1,[('pickup','a')], verbose=1)
    check_result(plan,False)

    plan = pyhop2.find_plan(state1,[('pickup','b')], verbose=1)
    check_result(plan,False)

    plan = pyhop2.find_plan(state1,[('pos','b','hand')], verbose=1)
    check_result(plan,False)

    pause()
    print("""
Next, some simple things that should succeed. As a reminder, in state1,
block a is on block b, block b is on the table, and block c is on the table.
""")
    
    plan = pyhop2.find_plan(state1,[('pickup','c')], verbose=1)
    check_result(plan, [('pickup','c')])

    plan = pyhop2.find_plan(state1,[('unstack','a','b')], verbose=1)
    check_result(plan, [('unstack','a', 'b')])

    plan = pyhop2.find_plan(state1,[('pos','a','hand')], verbose=1)
    check_result(plan, [('unstack','a', 'b')])

    plan = pyhop2.find_plan(state1,[('pos','c','hand')], verbose=1)
    check_result(plan, [('pickup','c')])

    plan = pyhop2.find_plan(state1,[('pos','a','table')], verbose=1)
    check_result(plan, [('unstack','a', 'b'), ('putdown','a')])
    pause()


    print("""
A Multigoal is a data structure that specifies desired values for some of the
state variables. In blocks_tasks.py there are examples of tasks whose arguments
are multigoals, but here we give the multigoals directly to find_plan.

Below, goal1a says we want the blocks in the configuration "c on b on a", and
goal1a says we want "c on b on a on the table". goal1a and goal1b have the same
set of solutions, because the "a on the table" will be achieved anyway.
""")

    state1.display("Initial state is")

    goal1a = pyhop2.Multigoal('goal1a')
    goal1a.pos={'c':'b', 'b':'a', 'a':'table'}

    goal1a.display()
    
    goal1b = pyhop2.Multigoal('goal1b')
    goal1b.pos={'c':'b', 'b':'a'}

    goal1b.display()

    expected = [('unstack', 'a', 'b'), ('putdown', 'a'), ('pickup', 'b'), ('stack', 'b', 'a'), ('pickup', 'c'), ('stack', 'c', 'b')] 

    plan1 = pyhop2.find_plan(state1,[goal1a], verbose=1)
    check_result(plan1,expected)

    plan2 = pyhop2.find_plan(state1,[goal1b], verbose=1)
    check_result(plan2,expected)
    pause()

    print("""
Run find_plan on two more planning problems. Like before, goal2a omits some
of the conditions in goal2a, but both goals should produce the same plan.
""")

    state2 = pyhop2.State('state2')
    state2.pos={'a':'c', 'b':'d', 'c':'table', 'd':'table'}
    state2.clear={'a':True, 'c':False,'b':True, 'd':False}
    state2.holding={'hand':False}

    state2.display('Initial state is')
    
    goal2a = pyhop2.Multigoal('goal2a')
    goal2a.pos={'b':'c', 'a':'d', 'c':'table', 'd':'table'}
    goal2a.clear={'a':True, 'c':False,'b':True, 'd':False}
    goal2a.holding={'hand':False}

    goal2a.display()
    
    goal2b = pyhop2.Multigoal('goal2b')
    goal2b.pos={'b':'c', 'a':'d'}

    goal2b.display()
    
    ### goal2b omits some of the conditions of goal2a,
    ### but those conditions will need to be achieved anyway.

    expected = [('unstack', 'a', 'c'), ('putdown', 'a'), ('unstack', 'b', 'd'), ('stack', 'b', 'c'), ('pickup', 'a'), ('stack', 'a', 'd')] 

    plan1 = pyhop2.find_plan(state2,[goal2a], verbose=1)
    check_result(plan1,expected)

    plan2 = pyhop2.find_plan(state2,[goal2b], verbose=1)
    check_result(plan2,expected)
    pause()


    print("\nRun find_plan on problem bw_large_d from the SHOP distribution:\n")

    state3 = pyhop2.State('state3')
    state3.pos = {1:12, 12:13, 13:'table', 11:10, 10:5, 5:4, 4:14, 14:15, 15:'table', 9:8, 8:7, 7:6, 6:'table', 19:18, 18:17, 17:16, 16:3, 3:2, 2:'table'}
    state3.clear = {x:False for x in range(1,20)}
    state3.clear.update({1:True, 11:True, 9:True, 19:True})
    state3.holding={'hand':False}

    state3.display('Initial state is')
    
    goal3 = pyhop2.Multigoal('goal3')
    goal3.pos = {15:13, 13:8, 8:9, 9:4, 4:'table', 12:2, 2:3, 3:16, 16:11, 11:7, 7:6, 6:'table'}
    goal3.clear = {17:True, 15:True, 12:True}

    goal3.display()
    
    expected = [('unstack', 1, 12), ('putdown', 1), ('unstack', 19, 18), ('putdown', 19), ('unstack', 18, 17), ('putdown', 18), ('unstack', 17, 16), ('putdown', 17), ('unstack', 9, 8), ('putdown', 9), ('unstack', 8, 7), ('putdown', 8), ('unstack', 11, 10), ('stack', 11, 7), ('unstack', 10, 5), ('putdown', 10), ('unstack', 5, 4), ('putdown', 5), ('unstack', 4, 14), ('putdown', 4), ('pickup', 9), ('stack', 9, 4), ('pickup', 8), ('stack', 8, 9), ('unstack', 14, 15), ('putdown', 14), ('unstack', 16, 3), ('stack', 16, 11), ('unstack', 3, 2), ('stack', 3, 16), ('pickup', 2), ('stack', 2, 3), ('unstack', 12, 13), ('stack', 12, 2), ('pickup', 13), ('stack', 13, 8), ('pickup', 15), ('stack', 15, 13)] 

    plan = pyhop2.find_plan(state3,[goal3], verbose=1)
    check_result(plan,expected)
    pause()

    print("""
Call run_lazy_lookahead on the following problem, with verbose=1:
""")

    state2.display(heading='Initial state is')
    goal2b.display(heading='Goal is')

    new_state = pyhop2.run_lazy_lookahead(state2, [goal2b], verbose=1)

    pause()

    print("The goal should now be satisfied, so the planner should return an empty plan:\n")

    plan = pyhop2.find_plan(new_state, [goal2b], verbose=1)
    check_result(plan,[])

    print("No more examples")

###############################################################################
# It's tempting to put a call to main() at this point, to run the examples
# without making the user type an extra command. But if we do this and an
# error occurs during execution of main(), we get a situation in which the
# actions and methods files have been imported but the current file hasn't
# been -- which causes problems if we try to import the current file again.
###############################################################################
