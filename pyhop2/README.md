# Pyhop 2

**Copyright &#169; 2021 [Dana S. Nau](http://www.cs.umd.edu/~nau)**

## Summary

Pyhop 2 is a planner based on [Pyhop](https://bitbucket.org/dananau/pyhop/). It is mostly backward-compatible, but not completely so. Pyhop 2 requires Python 3.

In addition to tasks as in Pyhop [1], Pyhop 2 adds the following:

  - goals (conditions that the planner is supposed to make true),
  - multigoals (conjunctions of individual goals),
  - methods for goals, and methods for multigoals,
  - example problem files for goals and multigoals,

These make it possible for Pyhop 2 to do HTN planning like Pyhop does, hierarchical goal network planning like GDP [2] does, and a mixture of both. [Remarks about HGN Planning in Pyhop 2](HGN_planning_in_Pyhop2.md) discusses some relevant details.

Pyhop 2 also includes the following additions:

  - An implementation of the Run-Lazy-Lookahead actor [1], and a way to declare commands that the actor can perform.
  - A new Domain class to hold all of a planning-and-acting domain's actions, commands, tasks, goals, and methods. This makes it possible to have several domains in memory the same time, without their interfering with each other.

All this has made the code more complicated. The Pyhop 2 source file is nearly four times as long as the one for Pyhop.

## Example files

Launch Python 3, and try loading each of the following:

- [`pyhop1_simple_travel_example.py`](pyhop1_simple_travel_example.py)
- [`simple_tasks.py`](simple_tasks.py)
- [`backtracking_tasks.py`](backtracking_tasks.py)
- [`blocks_tasks.py`](blocks_tasks.py)
- [`simple_goals.py`](simple_goals.py)
- [`blocks_goals.py`](blocks_goals.py)
- [`blocks_goal_splitting.py`](blocks_goal_splitting.py)


## Incompatibilities with Pyhop

Here are the ones I remember. If you find any that aren't in this list, please let me know.

- Unlike Pyhop, Pyhop 2 requires Python 3.
- pyhop.declare_operators is now called pyhop2.declare_actions.
- pyhop.print_operators is now called pyhop2.print_actions.
- pyhop.declare_methods is replaced by pyhop2.declare_task_methods, which is nearly the same but can be called more than once for the same taskname, to declare additional methods for that taskname.
- pyhop.pyhop is now called pyhop2.find_plan.
- pyhop.print_state(state) is replaced with state.display().
- pyhop.print_goal(goal) is replaced with goal.display().
- There is a new Domain class, to provide a place to store the various elements of a planning-and-acting domain (actions, methods, etc.). Before declaring any of those
things, one must first make a Domain instance to hold them.


## References

[1] D. Nau. [Game Applications of HTN Planning with State Variables](http://www.cs.umd.edu/~nau/papers/nau2013game.pdf). In *ICAPS Workshop on Planning in Games*, 2013. Keynote talk.

[2] V. Shivashankar, U. Kuter, D. S. Nau, and R. Alford. [A hierarchical goal-based formalism and algorithm for single-agent planning](https://www.cs.umd.edu/~nau/papers/shivashankar2012hierarchical.pdf). In *Proc. International Conference on Autonomous Agents and Multiagent Systems (AAMAS)*, 2012.

[3] M. Ghallab, D. S. Nau, and P. Traverso. [*Automated Planning and Acting*](http://www.laas.fr/planning). Cambridge University Press, Sept. 2016.