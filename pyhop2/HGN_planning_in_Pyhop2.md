## HGN planning in Pyhop 2

Dana Nau, University of Maryland

Feb 11, 2021

----------

In Pyhop 2's `find_plan`, a planning problem is specified by a *state* and a *todo list*, the latter being a list of actions, tasks, goals, and multigoals. Pyhop 2, like Pyhop 1, will apply an action only if it appears explicitly in the todo list. This differs from HGN (hierarchical goal network) planners such as GDP [1] and GoDel [2], in which a classical-planning action may be applied if all of its preconditions are satisfied, at least one of its effects matches one of the goals, and none of its effects negates any of the goals.

That isn't feasible in Pyhop 2, because Pyhop 2's actions are not classical. Rather than having fixed lists of preconditions and effects, a Pyhop 2 preconditions and effects are computed using arbitrary Python code. The only way to tell what effects an action will have is to try to apply the fully instantiated action in the current state, and see what state it produces.

Thus, to find an action that is applicable in a state *s* and whose effects satisfy a goal *g*, we would need to iterate through every possible action instance (i.e, every combination of action name and parameter values), to see if applying the action instance in *s* produces a state that satisfies *g*. Such a combinatorial explosion would be unacceptably expensive.

In Pyhop 2, one can get the same effect, with much less computational expense, by writing a small number of methods: one method for each of the action's effects. For example, consider an environment in which there is the following classical action for unloading a container `c` from a robot `r` at a location `l`. 

  - `unload(r,c,l)`:
    - precond: `loc[c]=r`, `cargo[r]=c`, `loc[r]=l`
    - effects: `loc[c]=l`, `cargo[r]=nil`
    
Then we can write two methods, one for each of the action's effects:

- A goal-method `m_loc(c,l)` that we declare relevant for the state-variable name `loc`, so that it can be used for goals of the form `loc[c]=l`.  In the current state, if `loc[c]` is a robot `r` and `r`'s location is `l`, this method will unload `c` from `r` using the action `unload(loc[c],c,l)`.

- A goal-method `m_cargo(r,v)` that we declare relevant for the state-variable name `cargo`, so that it can be used for goals of the form `cargo[r]=v`. If `v=nil`, and if `cargo[r]≠nil` in the current state, then this method will unload `r`'s cargo using the action `unload(r,cargo[r],loc[r])`.

If your domain definition includes such methods for all of the actions, then Pyhop 2 should behave somewhat similarly to GDP -- though not identically, since Pyhop 2 won't have access to the heuristic function that GDP uses to guide its search.

### Comparison with HGNpyhop.

There is a fork of Pyhop called [HGNpyhop](https://github.com/ospur/hgn-pyhop). Below I discuss two differences in how HGNpyhop and Pyhop 2 handle goals.

**1. Actions and goals.**
In HGNpyhop, one may declare an action to be directly relevant for a goal. At first glance, this seems like a desirable feature, and I seriously considered adding it to Pyhop 2 -- but I ultimately decided against it, for the reasons explained below.

For a goal of the form `state_variable_name[arg]=value`, [HGNpyhop](https://github.com/ospur/hgn-pyhop) would require each relevant action to be callable as `action_name(arg,value)`. Consider the following two cases:

 - To make `unload` relevant for goals of the form `loc[c]=l`, we would need to rewrite it to be callable as `unload(c,l)`, and declare it relevant for `loc`. The rewrite would need to look like the following, where `is_a` would be a helper function for determining an object's type:
 
  - `unload(c,l)`:
    - precond: `is_a(loc[c],'robot')`, `loc[loc[c]]=l`
    - effects: `cargo[loc[c]]=nil`, `loc[c]=l`

 - To make `unload` relevant for goals of the form `cargo[r]=v`, we would need to rewrite it to be callable as `unload(r,v)`, and declare it relevant for `cargo`. The rewrite would need to look like this:
 
  - `unload(r,v)`:
    - precond: `v = nil`, `cargo[r]≠nil`
    - effects: `loc[cargo[r]]=loc[r]`, `cargo[r]=nil`


Both rewrites seem a little awkward. To make HGNpyhop behave like GDP, HGNpyhop would somehow need to have *both* rewrites at once, even though they conflict with each other.

In Pyhop 2, we can easily make the `unload` action relevant for both goals, by writing the two methods described earlier. In my view, this is a better approach.

**2. Checking whether a method has achieved a goal.**
If *g* is a goal or multigoal, and *m* is a method that has been declared to be relevant for *g*, then *g* should be true upon 
completion of *m*. 
By default, when *m* finishes, Pyhop 2 will check whether *g* is true, and will backtrack if *g* is false.
HGNpyhop does not perform this check (or at least I didn't see it in the HGNpyhop code).

To perform this check, Pyhop 2 inserts into the todo list, immediately after the subtasks generated by *m*, a special task called `_verify_goal` or `_verify_multigoal`. In both cases, the task has just one method. Instead of generating subtasks, the method will check whether *g* is satisfied, and signal an error if it isn't.

An obvious question is whether such checks are useful. They might be useful while developing and debugging a domain, but the proliferation of  `_verify_goal` and `_verify_multigoal` tasks in the todo list adds overhead and interferes with readability of Pyhop 2's debugging printout. Thus one may prefer to turn them off -- which can be done by putting the following into the domain definition or at the beginning of a planning problem:

    `verify_goals(False)` 

Depending on feedback from users, I'll consider making `verify_goals(False)` the default.

---------

#### References ####

[1] V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS), 2012.

[2] V. Shivashankar, R. Alford, U. Kuter, and D. Nau. [The GoDeL planning system: A more perfect union of domain-independent and hierarchical planning](https://www.cs.umd.edu/~nau/papers/shivashankar2013godel.pdf). In Proc. International Joint Conference on Artificial Intelligence (IJCAI), pp. 2380–2386, 2013.