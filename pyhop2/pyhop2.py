"""
Pyhop 2, beta 3
This fixes a pretty big error in Pyhop 2, beta 2. It wasn't backtracking
properly, and none of the test files tested this. Beta 3 fixes that error,
and I've added a test file to illustrate how the backtracking should work.
Author: Dana Nau <nau@umd.edu>
Feb 22, 2021

Pyhop 2 is an enhanced version of Pyhop that can plan for both tasks and goals.
It requires Python 3. It isn't backward-compatible with Pyhop, but nearly is.
For an example, see the file pyhop1_simple_travel_example.py.

This file provides the following classes, functions, and variables. 
Use python's 'help' function to get information about each of them.

- classes and their methods: 
    Domain:    copy, display
    Multigoal: copy, display
    State:     copy, display

- functions:
    current_domain, set_current_domain, domains, remove_domain
    declare_actions
    declare_commands
    declare_goal_methods
    declare_multigoal_methods
    declare_task_methods
    find_plan
    get_type
    m_split_goals
    print_actions
    print_commands
    print_methods
    run_lazy_lookahead
    verify_goals

Accompanying this file are a README.md file that's an overview of Pyhop 2,
and several files to give examples of how to use Pyhop 2.
To run them, launch python and type one or more of the following:
import simple_tasks1
import simple_tasks2
import backtracking_tasks
import blocks_tasks
import simple_goals
import blocks_goals
import blocks_goal_splitting

"""

# For use in debugging:
# from IPython import embed
# from IPython.terminal.debugger import set_trace

import copy, sys, pprint

################################################################################
# States and goals

_next_state_number = 0

class State():
    """
    s = State(state_name,**kwargs) creates an object that is a container for
    a set of state-variable bindings that represent a state-of-the-world.
      - The argument 'state_name', which is optional, is the state's name.
        If you omit it, a name of the form _state# will be assigned, where
        # is an integer.
      - The keyword args are the names and initial values of state variables.
        A state-variable's initial value is usually {}, but it can also
        be a dictionary of arguments and their initial values.
    
    Example: here are three equivalent ways to specify a state named 'foo'
    in which boxes b and c are located in room2 and room3:
        First:
           s = State('foo')
           s.loc = {}   # create a dictionary for things like loc['b']
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Second:
           s = State('foo',loc={})
           s.loc['b'] = 'room2'
           s.loc['c'] = 'room3'
        Third:
           s = State('foo',loc={'b':'room2', 'c':'room3'})
    """
    def __init__(self,name=None,**kwargs):
        """
        If 'name' is given, then give the state that name. Otherwise, give it
        a name of the form '_state#' where # is an integer. The other keyword
        args are the names and initial values of state variables.
        """
        global _next_state_number
        if name:
            self.__name__ = name
        else:
            self.__name__ = f'_state{_next_state_number}'
            _next_state_number += 1
        vars(self).update(kwargs)
            
    def __str__(self):
        return self.__name__
        
    def __repr__(self):
        """Return a string that can be used to reconstruct the state"""
        x = f"State('{self.__name__}', "
        x += ', '.join([f'{v}={vars(self)[v]}' for v in vars(self) if v != '__name__'])
        x += ')'
        return x

    def nameless_repr(self):
        x = f"("
        x += ', '.join([f'{v}={vars(self)[v]}' for v in vars(self) if v != '__name__'])
        x += ')'
        return x

    def copy(self,name=None):
        """
        Make a copy of the state. If name is given, then give the copy that name.
        Otherwise give it a name of the form '_state#' where # is an integer.
        """
        global _next_state_number
        state = copy.deepcopy(self)
        if name:
            state.__name__ = name
        else:
            state.__name__ = f'_state{_next_state_number}'
            _next_state_number += 1
        return state

    def display(self,heading=None):
        """
        Print the state's state-variables and their values. The arguments are:
         - heading (optional) is a heading to print beforehand.
        """
        _print_state(self,heading=heading)

_next_multigoal_number = 0

class Multigoal():
    """
    g = Multigoal(goal_name,**kwargs) creates a Multigoal object that is a 
    container for state-variable bindings. It represents a conjunctive goal, 
    i.e., the goal of achieving every state-variable binding in g.
      - The optional argument 'goal_name' is the name to use for the goal.
        If you omit it, a name of the form _goal# will be assigned, where #
        is an integer.
      - The keyword args are name and initial values of state variables.
        A state variable's initial value is usually {}, but it can also
        be a dictionary of arguments and their initial values.

    Example: here are three equivalent ways to specify a goal named 'goal1'
    in which boxes b and c are located in room2 and room3:
        First:
           g = Multigoal('goal1')
           g.loc = {}   # create a dictionary for things like loc['b']
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Second:
           g = Multigoal('goal1', loc={})
           g.loc['b'] = 'room2'
           g.loc['c'] = 'room3'
        Third:
           g = Multigoal('goal1',loc={'b':'room2', 'c':'room3'})
    """
    def __init__(self,name=None):
        """
        If 'name' is given, then use it as the goal's name. Otherwise,
        give it a name of the form '_multigoal#' where # is an integer.
        """
        global _next_multigoal_number
        if name:
            self.__name__ = name
        else:
            self.__name__ = f'_multigoal{_next_multigoal_number}'
            _next_multigoal_number += 1
            
    def __str__(self):
        return f"<Multigoal {self.__name__}>"
        
    def __repr__(self):
        """Return a string that can be used to reconstruct the state"""
        x = f"Multigoal('{self.__name__}', "
        x += ', '.join([f'{v}={vars(self)[v]}' for v in vars(self) if v != '__name__'])
        x += ')'
        return x

    def copy(self,name=None):
        """
        Make a copy of the goal. If name is given, then give the copy that name.
        Otherwise give it a name of the form '_multigoal#' where # is an integer.
        """
        global _next_multigoal_number
        multigoal = copy.deepcopy(self)
        if name:
            multigoal.__name__ = name
        else:
            multigoal.__name__ = f'_multigoal{_next_multigoal_number}'
            _next_multigoal_number += 1
        return multigoal

    def display(self,heading=None):
        """
        Print the multigoal's state-variables and their values. The arguments are:
         - heading (optional) is a heading to print beforehand.
        """
        _print_state(self,heading=heading)


def _print_state(state,heading=None):
    """
    Print the state-variables and values in 'state', which may be
    either a state object or a goal object. The optional arguments are:
    - heading, a heading to print beforehand.
    """
    if heading == None: heading = get_type(state)
    if state != False:
        title = f"{heading} {state.__name__}:"
        dashes = '-'*len(title)
        print(title)
        print(dashes)
        for (varname,val) in vars(state).items():
            if varname != '__name__':
                print(f"  - {varname} = {val}")
        print('')
    else: 
        if heading == None: heading = 'state'
        print('{heading} = False','\n')


################################################################################
# A class for holding planning-and-acting domains.

class Domain():
    """
    d = Domain(domain_name,**kwargs) creates an object that is a container for
    all the actions, commands, task_methods, goal_methods, multigoals, and
    multigoal_methods associated with a planning-and-acting domain.

    If domain_name is given and there is already a domain with that name,
    the new one will replace it. If domain_name is omitted, the new domain
    will be given a name of the form _domain#, where # is a number. In both
    cases, the new domain will become the current domain.
    """

    def __init__(self,name=None):
        """
        If 'name' is given, then use it as the domain's name. Otherwise,
        give it a name of the form '_domain#' where # is an integer.
        """
        global _next_domain_number
        global _domain_dict, _current_domain
        
        if name:
            self.__name__ = name
        else:
            self.__name__ = f'_domain{_next_domain_number}'
            _next_domain_number += 1

        _domain_dict.update({name:self})
        _current_domain = self
        

        # dictionary that maps each action name to the corresponding function
        self._action_dict = {}   
        
        # dictionary that maps each action name to the corresponding cost
        self._action_cost_dict = {}    
            
        # dictionary that maps each command name to the corresponding function
        self._command_dict = {}
        
        # dictionary that maps each task name to a list of methods for the task
        self._task_method_dict = {'_verify_g': [_m_verify_g], '_verify_mg': [_m_verify_mg]}
        
        # dictionary that maps each goal name to a list of methods for the goal
        self._goal_method_dict = {}
        
        # list of all methods for multigoals
        self._multigoal_method_list = []

        _domain_dict.update({self.__name__:self})


    def __str__(self):
        return f"<Domain {self.__name__}>"
        
    def __repr__(self):
        """Return a string that can be used to reconstruct the domain"""
        x = f"Domain('{self.__name__}', "
        x += ', '.join([f'{v}={vars(self)[v]}' for v in vars(self) if v != '__name__'])
        x += ')'
        return x

    def copy(self,name=None):
        """
        Make a copy of the domain. If name is given, then give the copy that name.
        Otherwise give it a name of the form '_domain#' where # is an integer.
        """
        global next_domain_number
        dom = copy.deepcopy(self)
        if name:
            dom.__name__ = name
        else:
            dom.__name__ = f'_domain{next_domain_number}'
            next_domain_number += 1
        return dom
        

# If you call Domain() with no arguments, the new domain's name will be
# _domain#, where # is the following number.
_next_domain_number = 0


# The set of all domains that have been created
_domain_dict = {}


# A global variable telling the Pyhop 2 functions what domain we're using.
# At the end of this file, we'll set it to a newly created domain.
_current_domain = None


def current_domain():
    "Return the name of the current domain."
    return _current_domain.__name__


def set_current_domain(domain_name):
    """
    domain_name should be the name of a domain that has been defined using
    the Domain class. set_current_domain makes it the current domain.
    """
    global _current_domain
    domain = _domain_dict.get(domain_name)
    if domain == None:
        raise Exception(f"There is no domain named {domain_name}")
    _current_domain = _domain_dict[domain_name]


def domains():
    "Return the set of all domain names."
    return {name for name in _domain_dict}


def remove_domain(domain_name):
    "Remove the domain named domain_name from the set of all domains."
    if _current_domain == domain_name:
        raise Exception(f"Can't remove {domain.__name__}, because it's the current domain")
    else:
        _domain_dict.pop(domain_name)
    

################################################################################
# Commands for distinguishing data types


def get_type(object):
    "Return object's type name"
    return type(object).__name__


def _todo_to_string(todo):
    ttype = get_type(todo)
    if ttype == 'list':
        return str([str(x) for x in todo])
    elif ttype == 'tuple':
        return str(tuple([str(x) for x in todo]))
    else:
        return str(todo)


################################################################################
# Functions to declare actions, commands, tasks, goals, multigoals


def declare_actions(*actions):
    """
    Each member of actions must be a function name (not a string).
    declare_actions tells Pyhop 2 that each of them is an action. For
    example, this tells Pyhop 2 that pickup and putdown are actions:
        declare_actions(pickup,putdown)
    
    declare_actions can be called several times to declare more actions.
    """
    if _current_domain == None:
        raise Exception(f"cannot declare actions until a domain has been created.")
    _current_domain._action_dict.update({act.__name__:act for act in actions})
    for act in actions:
        _current_domain._action_cost_dict.setdefault(act.__name__, 1)
    return _current_domain._action_dict

def declare_actions_cost(*actions):
    if _current_domain == None:
        raise Exception(f"cannot declare actions until a domain has been created.")
    _current_domain._action_cost_dict.update({act.__name__:cost for (act, cost) in actions})
    return _current_domain._action_cost_dict

def declare_commands(*commands):
    """
    Each member of commands must be a function name (not a string), and the
    name should have the form c_foo, where foo is the name of an action.
    declare_commands tells Pyhop 2 that each of the functions is a command.
    Example: the following tells Pyhop 2 that c_pickup and c_putdown are
    commands:
        declare_commands(c_pickup,c_putdown)
    
    declare_commands can be called several times to declare more commands.
    """
    if _current_domain == None:
        raise Exception(f"cannot declare commands until a domain has been created.")
    _current_domain._command_dict.update({cmd.__name__:cmd for cmd in commands})
    return _current_domain._command_dict


def declare_task_methods(task_name, *task_methods):
    """
    task_name must be a character string, and each member of task_methods must
    be a function name (not a character string). declare_task_methods tells
    Pyhop 2 that each of the functions is a task_method that is relevant for
    every task of the form (task_name, arg1, ..., argn). Example:
        declare_task_methods('travel', travel_by_car, travel_by_foot)
    tells Pyhop that travel_by_car and travel_by_foot are methods and are 
    relevant for tasks such as these:
        ('travel', 'alice', 'store')
        ('travel', 'alice', 'umd', 'ucla')
        ('travel', 'alice', 'umd', 'ucla', 'slowly')
        ('travel', 'bob', 'home', 'park', 'looking', 'at', 'birds')

    This is similar to the original Pyhop's declare_methods function,
    except that declare_task_methods can be called several times to 
    declare more methods for the same task.
    """
    if _current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if task_name in _current_domain._task_method_dict:
        old_methods = _current_domain._task_method_dict[task_name]
        # even though _current_domain._task_method_dict[task_name] is a list,
        # we don't want to add any methods that are already in it
        new_methods = [m for m in task_methods if m not in old_methods]
        _current_domain._task_method_dict[task_name].extend(new_methods)
    else:
        _current_domain._task_method_dict.update({task_name:list(task_methods)})
    return _current_domain._task_method_dict


def declare_goal_methods(goal_name, *goal_methods):
    """
    goal_name must be a character string, and each member of goal_methods must
    be a function name (not a character string). declare_goal_methods tells
    Pyhop 2 that each of the functions is a goal_method that is relevant for
    every goal of the form (goal_name, arg, value). Example:
        declare_goal_method('loc',travel_by_car)
    tells Pyhop that travel_by_car is relevant for goals such as these:
        ('loc', 'alice', 'ucla')
        ('loc', 'bob', 'home')
    
    declare_goal_methods can be called several times to declare more
    methods for the same goal.
    """
    if _current_domain == None:
        raise Exception(f"cannot declare methods until a domain has been created.")
    if goal_name not in _current_domain._goal_method_dict:
        _current_domain._goal_method_dict.update({goal_name:list(goal_methods)})
    else:
        old_methods = _current_domain._goal_method_dict[goal_name]
        new_methods = [m for m in goal_methods if m not in old_methods]
        _current_domain._goal_method_dict[goal_name].extend(new_methods)
    return _current_domain._goal_method_dict    


def declare_multigoal_methods(*mg_methods):
    """
    declare_multigoal_methods tells Pyhop 2 that each member of mg_methods
    is a multigoal_method. Each member of mg_methods must be a function name
    (not a string). Example: the following tells Pyhop 2 that stack_all_blocks
    and unstack_all_blocks are multigoal_methods:
        declare_multigoal_methods(stack_all_blocks,unstack_all_blocks)

    declare_multigoal_methods can be called several times to declare
    more multigoal methods.
    """
    if _current_domain == None:
        raise Exception(    \
                f"cannot declare methods until a domain has been created.")
    new_mg_methods = [m for m in mg_methods if m not in \
                      _current_domain._multigoal_method_list]
    _current_domain._multigoal_method_list.extend(new_mg_methods)
    return _current_domain._multigoal_method_list    


################################################################################
# Functions to print information about the declared tasks, goals, etc.

def print_domain(heading='\nDomain name:'):
    """
    Print the domain's state-variables and their values. The arguments are:
     - heading (optional) is a heading to print beforehand.
    """
    print(f'{heading} {_current_domain.__name__}')
    print_actions()
    print_commands()
    print_methods()

def print_actions():
    """Print the names of all the actions"""
    if _current_domain._action_dict:
        print('-- Actions:', ', '.join(_current_domain._action_dict))
    else:
        print('-- There are no actions --')

def print_commands():
    """Print the names of all the commands"""
    if _current_domain._command_dict:
        print('-- Commands:', ', '.join(_current_domain._command_dict))
    else:
        print('-- There are no commands --')

def _print_task_methods():
    """Print a table of the task_methods for each task"""
    if _current_domain._task_method_dict:
        print('')
        print('Task name:         Relevant task methods:')
        print('---------------    ----------------------')
        for task in _current_domain._task_method_dict:
            print(f'{task:<19}' + ', '.join(    \
                [f.__name__ for f in _current_domain._task_method_dict[task]]))
        print('')
    else:
        print('-- There are no task methods --')

def _print_goal_methods():
    """Print a table of the goal_methods for each state_variable_name"""
    if _current_domain._goal_method_dict:
        print('State var name:    Relevant goal methods:')
        print('---------------    ----------------------')
        for var in _current_domain._goal_method_dict:
            print(f'{var:<19}' + ', '.join( \
                [f.__name__ for f in _current_domain._goal_method_dict[var]]))
        print('')
    else:
        print('-- There are no goal methods --')

def _print_multigoal_methods():
    """Print the names of all the multigoal_methods"""
    if _current_domain._multigoal_method_list:
        print('-- Multigoal methods:', ', '.join(  \
                [f.__name__ for f in _current_domain._multigoal_method_list]))
    else:
        print('-- There are no multigoal methods --')
    
def print_methods():
    """Print tables showing what all the methods are"""
    _print_task_methods()
    _print_goal_methods()
    _print_multigoal_methods()
    
################################################################################
# A built-in multigoal method and its helper function.


def m_split_goals(state,multigoal):
    """
    m_split_goals is the only multigoal method that Pyhop 2 provides, and
    Pyhop 2 won't use it unless the user declares it explicitly in a call
    to pyhop2.declare_multigoal_methods.
    
    m_split_goals takes two arguments: the current state and a multigoal
    to achieve. m_split_goals separates the multigoal into a collection of
    individual goals. Then it repeatedly iterates through the list of
    individual goals, trying to achieve each goal that isn't already true.
    The purpose of the repetition is to overcome deleted-condition
    interactions (in which accomplishing a goal has a side-effect of 
    falsifying another goal that was previously true).
    
    More specifically, if one or more of the individual goals is not true,
    then m_split_goals returns a goal list [g_1, ..., g_n, G], where
    g_1, ..., g_n are the goals that aren't true, and G is the multigoal.
    The list tells seek_plan to achieve g_1, ..., g_n sequentially, then
    invoke m_split_goals again to re-achieve any goals that have become
    false.

    The main problem with m_split_goals is that it isn't smart about
    choosing the order in which to achieve g1, ..., gn. Some orderings
    may work better than others. Thus it might be desirable to modify
    the method to use a heuristic function to choose a good order.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    goal_list = []
    for state_var_name in goal_dict:
        for arg in goal_dict[state_var_name]:
            val = goal_dict[state_var_name][arg]
            goal_list.append((state_var_name,arg,val))
    if goal_list:
        # achieve goals, then check whether they're all simultaneously true
        return goal_list + [multigoal]
    return goal_list


# helper function for m_split_goals above:

def _goals_not_achieved(state,multigoal):
    """
    _goals_not_achieved takes two arguments: a state s and a multigoal g.
    It returns a dictionary of the goals in g that aren't true in s.
    For example, suppose
        s.loc['c0'] = 'room0', g.loc['c0'] = 'room0',
        s.loc['c1'] = 'room1', g.loc['c1'] = 'room3',
        s.loc['c2'] = 'room2', g.loc['c2'] = 'room4'.
    Then _goals_not_achieved(s, g) will return
        {'loc': {'c1': 'room3', 'c2': 'room4'}}    
    """
    unachieved = {}
    for name in vars(multigoal):
        if name != '__name__':
            for arg in vars(multigoal).get(name):
                val = vars(multigoal).get(name).get(arg)
                if val != vars(state).get(name).get(arg):
                    # want arg_value_pairs.name[arg] = val
                    if not unachieved.get(name):
                        unachieved.update({name:{}})
                    unachieved.get(name).update({arg:val})
    return unachieved


################################################################################
# Functions to verify whether goal_method and multigoal_methods achieve the
# goals they are supposed to achieve.


_verify_goals = True


def verify_goals(boolean=None):
    """
    If boolean is True, then whenever the planner uses a method m to refine
    a goal or multigoal, it will insert a "verification" task into the
    current partial plan. If boolean is False, the planner won't insert
    any verification tasks into the plan. If verify_goals is call with no
    argument, it will return the current value of boolean.
    
    The purpose of the verification task is to raise an exception if the
    refinement produced by m doesn't achieve the goal or multigoal that it
    is supposed to achieve. This won't insert anything into the final plan;
    it just will verify whether m did what it was supposed to do.
    """
    global _verify_goals
    if boolean != None:
        _verify_goals = boolean
    return _verify_goals



def _m_verify_g(state, method_name, state_var_name, arg, desired_val, \
        depth, verbose=0):
    """
    Pyhop 2 uses this method to check whether a goal_method has achieved the
    goal that it promised to achieve.
    """
    if vars(state)[state_var_name][arg] != desired_val:
        raise Exception(f"depth {depth}: method {method_name} didn't achieve",
                f"goal {state_var_name}[{arg}] = {desired_val}")
    if verbose >= 3:
        print(f"depth {depth}: method {method_name} achieved",
                f"goal {state_var_name}[{arg}] = {desired_val}")
    return []       # i.e., don't create any subtasks or subgoals


def _m_verify_mg(state, method_name, multigoal, depth, verbose=0):
    """
    Pyhop 2 uses this method to check whether a multigoal-method has achieved
    the multigoal that it promised to achieve.
    """
    goal_dict = _goals_not_achieved(state,multigoal)
    if goal_dict:
        raise Exception(f"depth {depth}: method {method_name} " + \
                        f"didn't achieve {multigoal}]")
    if verbose >= 3:
        print(f"depth {depth}: method {method_name} achieved {multigoal}")
    return []


################################################################################
# Applying actions and commands
#
# An action is applied only if the task name is the name of the action.
# This differs from HGN planners such as GDP and Godel, in which we can
# decide which actions are relevant by matching their "effects" atoms with
# the goal atoms. That isn't feasible in Pyhop 2.
#
# The problem is that in Pyhop 2, the only way to tell what effects an
# action will have is to try to apply the fully instantiated action.
# Thus, to find an action that is applicable in a state s and whose effects
# satisfy a goal g, we would need to iterate through every possible action
# instance (i.e, every combination of action name and parameter values), to
# see if applying the action instance in s produces a state that satisfies
# g. Such a combinatorial explosion would be unacceptably expensive.
#
# In Pyhop 2, one can get the same effect, with much less computational
# expense, as follows. Consider a blocks-world action unstack(hand,b1,b2)
# that has three effects: loc(b1)=hand, holding(hand)=b1, and
# the-block-on(b2)=nil. Then we can write three methods:
# - a method m1(b1,new_loc) that's declared relevant for 'loc'. If
#   called with new_loc = hand, it calls unstack(hand,b1,state.loc(b1)).
# - a method m2(hand,b1) that's declared relevant for 'holding'.
#   It calls unstack(hand,b1,state.loc(b1)).
# - a method m3(b2,status) that's declared relevant for 'clear'. If
#   called with status=nil, it calls unstack(hand,the-block-on(b2),b2)).
#
# In hgn_pyhop <https://github.com/ospur/hgn-pyhop>, unlike Pyhop 2, one
# may declare actions to be directly relevant for goals. I considered
# adding this feature to Pyhop 2, but decided against it. For a goal of the
# form g = (name, arg, val), it would require restricting each relevant
# action to have exactly two parameters, one corresponding to arg and the
# other corresponding to val. Suppose we try to do this with the action
# unstack(hand,b1,b2) described above. To make it relevant for the goal
# loc(b1)=hand, we would need to rewrite it to take two parameters:
# b1 and hand.  If we instead wanted to make it relevant for the goal
# holding(hand,b1), or the goal atop(b2,nil), we would need
# to rewrite the action so its parameters can be hand and b1, or
# b2 and nil, respectively. All three of these are a bit unnatural --
# and furthermore there's no way to accomplish all three of them at
# once, which is what the GDP and Godel HGN planning algorithms would
# require. In contrast, in the current Pyhop 2 we can easily get the
# same effect by writing the three goal_methods described earlier.
# In my view, this is a better approach.
################################################################################


def _apply_action(state, task1, more_tasks, plan, depth, verbose=0):
    """
    apply_action is called only when task1's name matches an action name.
    It applies the action by retrieving the action's function definition
    and calling it on the arguments.
    """
    if verbose >= 3: print(f'depth {depth} action {task1}: apply action')
    action = _current_domain._action_dict[task1[0]]
    newstate = action(state.copy(),*task1[1:])
    if verbose >= 3:
        print(f'depth {depth}', end=' ')
        print(repr(newstate))
    if newstate:
        return seek_plan(newstate, more_tasks, plan+[task1], depth+1, verbose)
    if verbose >= 3: print(f'depth {depth} action {task1} not applicable')
    return False


def _apply_command(state, command, args, verbose=1):
    """
    apply_command is called only when task1's name matches a command name.
    It applies the command by retrieving the command's function definition
    and calling it on the arguments.
    """
    if verbose >= 3:
        print(f"_apply_command: state = {state.__name__},", \
              f"command = {command.__name__}, args = {args}")
    next_state = command(state.copy(),*args)
    if next_state:
        if verbose >= 3:
            print(f"_apply_command: {command.__name__}", \
                  f"returns state {next_state.__name__}")
        return next_state
    else:
        if verbose >= 3:
            print(f"_apply_command: {command.__name__} not applicable")
        return False

################################################################################
# Applying methods


def _find_task_method(state, task1, more_tasks, plan, depth, verbose=0):
    """
    if task1's name has an entry in the task-method dictionary, iterate
    through the methods until we find one that's applicable, then apply
    it to produce a list of subtasks, and call seek_plan recursively on
    the subtask list + more_tasks.
    If seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3: 
        print(f'depth {depth} task {task1}: look for a task method')
    relevant = _current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        print(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} task {task1}: trying method {method.__name__}')
        subtasks = method(state,*task1[1:])
        # Can't just say "if subtasks:", because that's wrong if subtasks == []
        if subtasks != False and subtasks != None:
            if verbose >= 3:
                print(f'depth {depth} task_method {method.__name__}', \
                      f'subtasks: {subtasks}')
            result = seek_plan(state, subtasks+more_tasks, plan, depth+1, verbose)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'depth {depth}', \
                      f'task_method {method.__name__} not applicable')
    if verbose >= 3:
        print(f'depth {depth} could not accomplish task {task1}')        
    return False


def _find_goal_method(state, goal1, more_goals, plan, depth, verbose=0):
    """
    if goal1's name has an entry in the goal-method dictionary, iterate
    through the methods until we find one that's applicable, then apply
    it to produce a list of subgoals, and call seek_plan recursively on
    the subgoal list + [verification] + more_goals, where verification is a
    special goal to test whether the method actually achieved goal1.
    If seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3:
        print(f'depth {depth} goal {goal1}: look for a goal method')
    (state_var_name, arg, val) = goal1
    if vars(state).get(state_var_name).get(arg) == val:
        if verbose >= 3:
            print(f'depth {depth} goal {goal1} is already achieved')
        return seek_plan(state, more_goals, plan, depth+1, verbose)
    relevant = _current_domain._goal_method_dict[state_var_name]
    if verbose >= 3:
        print(f'depth {depth} goal {goal1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} goal {goal1}: trying method {method.__name__}')
        subgoals = method(state,arg,val)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print(f'depth {depth} goal_method', \
                      f'{method.__name__} subgoals: {subgoals}')
            if _verify_goals:
                verification = [('_verify_g', method.__name__, \
                                 state_var_name, arg, val, depth, verbose)]
            else:
                verification = []
            todo_list = subgoals + verification + more_goals
            result = seek_plan(state, todo_list, plan, depth+1, verbose)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'depth {depth}', \
                      f'goal_method {method.__name__} not applicable')        
    if verbose >= 3:
        print(f'depth {depth} goal_method {method.__name__}', \
              f'could not achieve goal {goal1}')        
    return False


def _find_multigoal_method(state, multigoal1, more_goals, plan, depth, verbose=0):
    """
    if multigoal1 is a multigoal, iterate though the multigoal methods
    until we find one that's applicable, then apply it to get a subgoal
    list, and call seek_plan recursively on the subgoal list + more_goals.
    If seek_plan fails, go on to the next multigoal method. Unlike with
    goal methods, we don't do verification here because it's unclear what
    we're supposed to verify.
    """
    if verbose >= 3:
        print(f'depth {depth} multigoal {multigoal1}:', \
              f'look for a multigoal method')
    relevant = _current_domain._multigoal_method_list
    if verbose >= 3:
        print(f'depth {depth} multigoal {multigoal1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} task {multigoal1}: trying method {method.__name__}')
        subgoals = method(state,multigoal1)
        # Can't just say "if subgoals:", because that's wrong if subgoals == []
        if subgoals != False and subgoals != None:
            if verbose >= 3:
                print(f'depth {depth} multigoal_method {method.__name__}', \
                      f'subgoals: {subgoals}')
            if _verify_goals:
                verification = [('_verify_mg', method.__name__, multigoal1, \
                                 depth, verbose)]
            else:
                verification = []
            todo_list = subgoals + verification + more_goals
            result = seek_plan(state, todo_list, plan, depth+1, verbose)
            if result != False and result != None:
                return result
        else:
            if verbose >= 3:
                print(f'depth {depth} multigoal_method {method.__name__}', \
                      f'not applicable')
    if verbose >= 3:
        print(f'depth {depth} could not achieve multigoal {multigoal1}')        
    return False


############################################################
# The planning algorithm


def find_plan(state, todo_list, verbose=0):
    """
    find_plan tries to find a plan that accomplishes the items in todo_list,
    starting from the given state, using whatever methods and actions you 
    declared previously. If successful, it returns the plan. Otherwise it
    returns False. Arguments:
     - 'state' is a state;
     - 'todo_list' is a list to-dos (tasks, goals, and multigoals);
     - verbose = 0, 1, 2, or 3 indicates how much debugging info to print:
        - if verbose = 0 (the default), it prints nothing;
        - if verbose = 1, it prints the initial parameters and the answer;
        - if verbose = 2, it also prints a message on each recursive call;
        - if verbose = 3, it also prints info about what it's computing.
    """
    if verbose >= 1: 
        todo_list_str =     \
            '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
        print(f'FP> find_plan, verbose={verbose}:')
        print(f'    state = {state.__name__}\n    todo_list = {todo_list_str}')
    result = seek_plan(state, todo_list, [], 0, verbose)
    if verbose >= 1: print('FP> result =',result,'\n')
    return result


def seek_plan(state, todo_list, plan, depth, verbose=0):
    """
    Workhorse for find_plan. Arguments:
     - state is the current state;
     - todo_list is the current list to-dos (tasks, goals, and multigoals);
     - plan is the current partial plan;
     - depth is the recursion depth, for use in debugging;
     - verbose = 0, 1, 2, or 3 indicates how much debugging info to print.
       For details, see the docstring for find_plan.
    """
    if verbose >= 2: 
        todo_list_str =     \
                '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
        print(f'depth {depth} todo_list ' + todo_list_str)
    if todo_list == []:
        if verbose >= 3:
            print(f'depth {depth} no more tasks or goals, return plan')
        return plan
    todo1 = todo_list[0]
    ttype = get_type(todo1)
    if ttype in {'list','tuple'}:
        if todo1[0] in _current_domain._action_dict:
            return _apply_action(state, todo1, todo_list[1:], \
                                 plan, depth, verbose=verbose)
        elif todo1[0] in _current_domain._task_method_dict:
            return _find_task_method(state, todo1, todo_list[1:], \
                                     plan, depth, verbose=verbose)
        elif todo1[0] in _current_domain._goal_method_dict:
            return _find_goal_method(state, todo1, todo_list[1:], \
                                     plan, depth, verbose=verbose)
    elif ttype in {'Multigoal'}:
        return _find_multigoal_method(state, todo1, todo_list[1:], \
                                      plan, depth, verbose=verbose)

    raise Exception(    \
        f"depth {depth}: {todo1} isn't an action, task, goal, or multigoal\n")
    return False


################################################################################
# An actor


def run_lazy_lookahead(state, todo_list, verbose=1, max_tries=10):
    """
    An adaptation of the run_lazy_lookahead algorithm from Ghallab et al.
    (2016), Automated Planning and Acting. It works roughly like this:
        loop:
            plan = find_plan(state, todo_list, verbose)
            if plan = []:
                return state    // the new current state 
            for each action in plan:
                execute the corresponding command
                if the command fails:
                    continue the outer loop
    Arguments: 
      - 'state' is a state;
      - 'todo_list' is a list of tasks, goals, and multigoals;
      - verbose = 0, 1, 2, or 3 indicates how much feedback will be given
        to the user. For details, see find_plan's docstring.
      - max_tries is a bound on how many times to execute the outer loop.
      
    Note: whenever run_lazy_lookahead encounters an action for which there is
    no corresponding command definition, it uses the action definition instead.
    """
    
    if verbose >= 1: 
        print(f"RLL> run_lazy_lookahead, verbose = {verbose}, max_tries = {max_tries}")
        print(f"RLL> initial state: {state.__name__}")
        print('RLL> To do:', todo_list)

    for tries in range(1,max_tries+1):
        if verbose >= 1: 
            ordinals = {1:'st',2:'nd',3:'rd'}
            if ordinals.get(tries):
                print(f"RLL> {tries}{ordinals.get(tries)} call to find_plan:\n")
            else:
                print(f"RLL> {tries}th call to find_plan:\n")
        plan = find_plan(state, todo_list, verbose=verbose)
        if plan == False or plan == None:
            if verbose >= 1:
                raise Exception(
                        f"run_lazy_lookahead: find_plan has failed")
            return state
        if plan == []:
            if verbose >= 1: 
                print(f'RLL> Empty plan => success',
                      f'after {tries} calls to find_plan.')
            if verbose >= 2: state.display(heading='> final state')
            return state
        for action in plan:
            command_name = 'c_' + action[0]
            command_func = _current_domain._command_dict.get(command_name)
            if command_func == None:
                if verbose >= 1: 
                    print(f'RLL> {command_name} not defined, using {action[0]} instead\n')
                command_func = _current_domain._action_dict.get(action[0])
                
            if verbose >= 1:
                print('RLL> Command:', [command_name] + list(action[1:]))
            new_state = _apply_command(state, command_func, \
                                       action[1:], verbose=verbose)
            if new_state == False:
                if verbose >= 1: 
                    print(f'RLL> WARNING: command {command_name} failed; will call find_plan.')
                    break
            else:
                if verbose >= 2: 
                    new_state.display()
                state = new_state
        # if state != False then we're here because the plan ended
        if verbose >= 1 and state:
            print(f'RLL> Plan ended; will call find_plan again.')
        
    if verbose >= 1: print('RLL> Too many tries, giving up.')
    if verbose >= 2: state.display(heading='RLL> final state')
    return state


###############################################################################
# GBFS
import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.time = 0
            
    def pop(self):
        value, _, item = heapq.heappop(self.heap)
        return (value, item)

    def push(self, value, item):
        heapq.heappush(self.heap, (value, self.time, item))
        self.time += 1


def history_string(state, tasks):
    return state.nameless_repr() + repr(tasks[0]) if tasks else ''

def _apply_action_GBFS(plans, state, task1, more_tasks, plan, depth, h, history, cost, c, a_star, verbose=0):
    """
    apply_action is called only when task1's name matches an action name.
    It applies the action by retrieving the action's function definition
    and calling it on the arguments.
    """
    if verbose >= 3: print(f'depth {depth} action {task1}: apply action')
    action = _current_domain._action_dict[task1[0]]
    newstate = action(state.copy(),*task1[1:])
    if newstate:
        history_str = history_string(newstate, more_tasks)
        if history_str in history:
            if verbose >= 3:
                print(f'depth {depth}', end=' ')
                print(repr(newstate) + ' repeated, not put into queue')
        else:
            history[history_str] = True
            h_new = h(newstate, more_tasks)
            c_new = cost + c(newstate)
            if a_star:
                h_new += c_new
            if verbose >= 3:
                print(f'depth {depth}', end=' ')
                print(repr(newstate) + ' with heuristic ' + str(h_new))
            plans.push(h_new, (newstate, more_tasks, plan+[task1], c_new, depth+1))
    elif verbose >= 3: print(f'depth {depth} action {task1} not applicable')

def _find_task_method_GBFS(plans, state, task1, more_tasks, plan, depth, h, history, cost, c, a_star, verbose=0):
    """
    if task1's name has an entry in the task-method dictionary, iterate
    through the methods until we find one that's applicable, then apply
    it to produce a list of subtasks, and call seek_plan recursively on
    the subtask list + more_tasks.
    If seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3: 
        print(f'depth {depth} task {task1}: look for a task method')
    relevant = _current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        print(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} task {task1}: trying method {method.__name__}')
        subtasks = method(state,*task1[1:])
        # Can't just say "if subtasks:", because that's wrong if subtasks == []
        if subtasks != False and subtasks != None:
            new_todo = subtasks+more_tasks
            history_str = history_string(state, new_todo)
            if history_str in history:
                if verbose >= 3:
                    print(f'depth {depth} task_method {method.__name__}', \
                          f'subtasks: {subtasks} repeated, not put into queue')
            else:
                history[history_str] = True
                h_new = h(state, new_todo)
                c_new = cost + c(state)
                if a_star:
                    h_new += c_new
                if verbose >= 3:
                    print(f'depth {depth} task_method {method.__name__}', \
                          f'subtasks: {subtasks} put into queue with heuristic {h_new}')
                plans.push(h_new, (state, new_todo, plan, c_new, depth+1))
        else:
            if verbose >= 3:
                print(f'depth {depth}', \
                      f'task_method {method.__name__} not applicable')

def find_plan_GBFS(state, todo_list, h, c=lambda s: 1, a_star=False, verbose=0):
    """
    h is heuristic. Takes two arguments: state and todo-list
    """
    if verbose >= 1: 
        todo_list_str =     \
            '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
        print(f'FP> find_plan, verbose={verbose}:')
        print(f'    state = {state.__name__}\n    todo_list = {todo_list_str}')
    plans = PriorityQueue()
    plans.push(0, (state, todo_list, [], 0, 0))
    result = seek_plan_GBFS(plans, h, c, {history_string(state, todo_list): True}, a_star, verbose)
    if verbose >= 1: print('FP> result =',result,'\n')
    return result


def seek_plan_GBFS(plans, h, c, history, a_star, verbose=0):
    """
    plans is a priority queue with (state, todo_list, plan, depth) tuples sorted by heuristic
    """
    while plans:
        h_pop, (state, todo_list, plan, cost, depth) = plans.pop()
        if verbose >= 2: 
            todo_list_str =     \
                    '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
            print(f'depth {depth} todo_list ' + todo_list_str + f' popped with heuristic {h_pop}')
        if todo_list == []:
            if verbose >= 3:
                print(f'depth {depth} no more tasks or goals, return plan')
            return plan
        todo1 = todo_list[0]
        ttype = get_type(todo1)
        if ttype in {'list','tuple'}:
            if todo1[0] in _current_domain._action_dict:
                _apply_action_GBFS(plans, state, todo1, todo_list[1:], \
                                plan, depth, h, history, cost, c, a_star, verbose=verbose)
            elif todo1[0] in _current_domain._task_method_dict:
                _find_task_method_GBFS(plans, state, todo1, todo_list[1:], \
                                    plan, depth, h, history, cost, c, a_star, verbose=verbose)
        else:
            raise Exception(    \
                f"depth {depth}: {todo1} isn't an action, task, goal, or multigoal\n")
    return False

###############################################################################
# A*
import heapq

def current_cost(plan):
    cost = 0
    for item in plan:
        cost = cost + _current_domain._action_cost_dict[item[0]]
    return cost

def _apply_action_a_star(plans, state, task1, more_tasks, plan, depth, h, history, verbose=0):
    """
    apply_action is called only when task1's name matches an action name.
    It applies the action by retrieving the action's function definition
    and calling it on the arguments.
    """
    if verbose >= 3: print(f'depth {depth} action {task1}: apply action')
    action = _current_domain._action_dict[task1[0]]
    newstate = action(state.copy(),*task1[1:])
    if newstate:
        history_str = history_string(newstate, more_tasks)
        if history_str in history:
            if verbose >= 3:
                print(f'depth {depth}', end=' ')
                print(repr(newstate) + ' repeated, not put into queue')
        else:
            history[history_str] = True
            h_new = h(newstate, more_tasks)
            h_old = current_cost(plan)
            h_use = h_new + h_old
            if verbose >= 3:
                print(f'depth {depth}', end=' ')
                print(repr(newstate) + ' with heuristic ' + str(h_new))
            plans.push(h_use, (newstate, more_tasks, plan+[task1], depth+1))
    elif verbose >= 3: print(f'depth {depth} action {task1} not applicable')

def _find_task_method_a_star(plans, state, task1, more_tasks, plan, depth, h, history, verbose=0):
    """
    if task1's name has an entry in the task-method dictionary, iterate
    through the methods until we find one that's applicable, then apply
    it to produce a list of subtasks, and call seek_plan recursively on
    the subtask list + more_tasks.
    If seek_plan fails, go on to the next method in the list.
    """
    if verbose >= 3: 
        print(f'depth {depth} task {task1}: look for a task method')
    relevant = _current_domain._task_method_dict[task1[0]]
    if verbose >= 3:
        print(f'depth {depth} task {task1} methods {[m.__name__ for m in relevant]}')
    for method in relevant:
        if verbose >= 3: 
            print(f'depth {depth} task {task1}: trying method {method.__name__}')
        subtasks = method(state,*task1[1:])
        # Can't just say "if subtasks:", because that's wrong if subtasks == []
        if subtasks != False and subtasks != None:
            new_todo = subtasks+more_tasks
            history_str = history_string(state, new_todo)
            if history_str in history:
                if verbose >= 3:
                    print(f'depth {depth} task_method {method.__name__}', \
                          f'subtasks: {subtasks} repeated, not put into queue')
            else:
                history[history_str] = True
                h_new = h(state, new_todo)
                h_old = current_cost(plan)
                h_use = h_new + h_old
                if verbose >= 3:
                    print(f'depth {depth} task_method {method.__name__}', \
                          f'subtasks: {subtasks} put into queue with heuristic {h_new}')
                plans.push(h_use, (state, new_todo, plan, depth+1))
        else:
            if verbose >= 3:
                print(f'depth {depth}', \
                      f'task_method {method.__name__} not applicable')

def find_plan_a_star(state, todo_list, h, verbose=0):
    """
    h is heuristic. Takes two arguments: state and todo-list
    """
    if verbose >= 1: 
        todo_list_str =     \
            '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
        print(f'FP> find_plan, verbose={verbose}:')
        print(f'    state = {state.__name__}\n    todo_list = {todo_list_str}')
    plans = PriorityQueue()
    #f(n) = 0 here, only g(n) needed
    plans.push(h(state, todo_list), (state, todo_list, [], 0))
    result = seek_plan_a_star(plans, h, {history_string(state, todo_list): True}, verbose)
    if verbose >= 1: print('FP> result =',result,'\n')
    return result


def seek_plan_a_star(plans, h, history, verbose=0):
    """
    plans is a priority queue with (state, todo_list, plan, depth) tuples sorted by heuristic
    """
    while plans:
        h_pop, (state, todo_list, plan, depth) = plans.pop()
        if verbose >= 2: 
            todo_list_str =     \
                    '[' + ', '.join([_todo_to_string(x) for x in todo_list]) + ']'
            print(f'depth {depth} todo_list ' + todo_list_str + f' popped with heuristic {h_pop}')
        if todo_list == []:
            if verbose >= 3:
                print(f'depth {depth} no more tasks or goals, return plan')
            return plan
        todo1 = todo_list[0]
        ttype = get_type(todo1)
        if ttype in {'list','tuple'}:
            if todo1[0] in _current_domain._action_dict:
                _apply_action_a_star(plans, state, todo1, todo_list[1:], \
                                plan, depth, h, history, verbose=verbose)
            elif todo1[0] in _current_domain._task_method_dict:
                _find_task_method_a_star(plans, state, todo1, todo_list[1:], \
                                    plan, depth, h, history, verbose=verbose)
        else:
            raise Exception(    \
                f"depth {depth}: {todo1} isn't an action, task, goal, or multigoal\n")
    return False




###############################################################################
# Create an initial domain. I would have preferred to locate this near the
# definition of the Domain class, but it must come after the built-in
# methods since the domain initialization refers to them.

_current_domain = Domain()       # create an initial domain