"""
Some examples that show Pyhop 2 backtracking over several goals and methods.
Author: Dana Nau <nau@umd.edu>
Feb 22, 2021
"""
import pyhop2


# Create a new domain that has the same name as this file. This avoids having
# to explicitly change the domain name every time I change the filename.
domain_name = __name__
pyhop2.Domain(domain_name)

###############################################################################
# States:

state0 = pyhop2.State()
state0.flag = -1


###############################################################################
# Methods:


def m_err(state):
    return [('putv', 0), ('getv', 1)]

def m0(state):
    return [('putv', 0), ('getv', 0)]

def m1(state):
    return [('putv', 1), ('getv', 1)]

pyhop2.declare_task_methods('put_it',m_err,m0,m1)


def m_need0(state):
    return [('getv', 0)]

def m_need1(state):
    return [('getv', 1)]

pyhop2.declare_task_methods('need0',m_need0)

pyhop2.declare_task_methods('need1',m_need1)

pyhop2.declare_task_methods('need01',m_need0,m_need1)

pyhop2.declare_task_methods('need10',m_need1,m_need0)

###############################################################################
# Actions:

def putv(state,flag_val):
    state.flag = flag_val
    return state

def getv(state,flag_val):
    if state.flag == flag_val:
        return state

pyhop2.declare_actions(putv,getv)

###############################################################################
# Problem:


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

    # two possible expected answers for check_result
    expect0 = [('putv', 0), ('getv', 0), ('getv', 0)]
    expect1 = [('putv', 1), ('getv', 1), ('getv', 1)]

    print("-- Four examples with verbose=3 to get a detailed account of the backtracking.")
    # Below, the comma after each task name is so Python will parse the task
    # as a tuple rather than an atom
    result = pyhop2.find_plan(state0,[('put_it',),('need0',)],verbose=3)
    check_result(result,expect0)
    print("""Above, seek_plan backtracks once to use a different method for 'put_it'.
""")
    pause()
    result = pyhop2.find_plan(state0,[('put_it',),('need01',)],verbose=3)
    check_result(result,expect0)
    print("""The backtracking in the above example is the same as in the first one.
""")
    pause()
    result = pyhop2.find_plan(state0,[('put_it',),('need10',)],verbose=3)
    check_result(result,expect0)
    print("""Above, seek_plan backtracks to use a different method for 'put_it',
and later it backtracks to use a different method for 'need10'.
""")    
    pause()
    result = pyhop2.find_plan(state0,[('put_it',),('need1',)],verbose=3)
    check_result(result,expect1)
    print("""First, seek_plan backtracks to use a different method for 'put_it'. But the
solution it finds for 'put_it' doesn't satisfy the preconditions of the method
for 'need1', making it backtrack to use a third method for 'put_it'.
""")    
