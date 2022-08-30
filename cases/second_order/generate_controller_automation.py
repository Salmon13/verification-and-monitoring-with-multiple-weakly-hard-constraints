import os
import random
import math
import yaml
import sys

def generate_automaton(x_min, x_max, x_interval, v_min, v_max, v_interval, a, dx_atk):
    '''
    Input:
        x_min (int): min limit of x (exceed = out of bound)
        x_max (int): max limit of x (exceed = out of bound)
        x_interval (int): interval of x to linspace between [x_min, x_max]
        v_min (int): min limit of v (exceed = capped at v_min)
        v_max (int): max limit of v (exceed = capped at v_max)
        v_interval (int): interval of v to linspace between [v_min, v_max]
        a (int): acceleration magnitude
    Output:
        automaton (list(dict{state, transition})):
            state (tuple(int, int, int)): (x, v, a)
            transitions (dict(string: list(tuple(int, int, int)))):
                map signal to list of transitioned states
    '''
    assert((x_max - x_min) % x_interval == 0)
    assert((v_max - v_min) % v_interval == 0)

    default_unsafe_state = (None, None, None)

    x = list(range(x_min, x_max + v_interval, x_interval))
    v = list(range(v_min, v_max + v_interval, v_interval))

    automaton = [{
        'state': default_unsafe_state,
        'transitions': [default_unsafe_state, default_unsafe_state],
        'safe': False
    }]

    for x_ in x:
        for v_ in v:
            for a_ in [-a, 0, a]:
                state = (x_, v_, a_)
                transitions = calculate_transitions(state, x_min, x_max,
                                                    v_min, v_max, a, dx_atk,
                                                    default_unsafe_state)
                vertex = {
                    'state': state,
                    'transitions': transitions,
                    'safe': True
                }
                automaton.append(vertex)

    return automaton

def calculate_transitions(state, x_min, x_max, v_min, v_max, a, dx_atk, default_unsafe_state):
    '''
    Input:
        state (tuple(int, int, int)): (x, v, a)
    Output:
        transitions (tuple(tuple(int, int, int), tuple(int, int, int))):
            list of transitioned states for 0 and 1
    '''
    clamp_v = lambda v: min(max(v, v_min), v_max)
    sign = lambda x: 0 if x == 0 else int(math.copysign(1, x))
    is_safe = lambda x: x >= x_min and x <= x_max

    x_pre, v_pre, a_pre, = state

    transitions = []

    for signal in [0, 1]:
        t_res = abs(v_pre) // a
        x_res = v_pre * t_res + 0.5 * a * t_res**2

        x_atk = x_pre + signal * dx_atk

        x_nxt = x_atk + v_pre
        v_nxt = clamp_v(v_pre + a_pre)
        a_nxt = -sign(x_atk) * sign(abs(x_atk) - abs(x_res)) * a

        if is_safe(x_nxt):
            transition = (x_nxt, v_nxt, a_nxt)
        else:
            transition = default_unsafe_state

        transitions.append(transition)

    return tuple(transitions)
def DFS(automaton, state, state2index, reached):
    reached[state2index[str(state)]] = 1
    #print(automaton[state2index[str(state)]])
    for tran in automaton[state2index[str(state)]]['transitions']:
        if not reached[state2index[str(tran)]]:
            DFS(automaton, tran, state2index, reached)
    return
def export_automaton(automaton, f, start_state=None):
    # set start state
    if start_state is None:
        start_state = (0, 0, 0)
    # move start state to front
    start_index = [i for i, v in enumerate(automaton)
                   if v['state'] == start_state][0]
    automaton.insert(0, automaton.pop(start_index))
    # construct dict: state -> index
    state2index = {str(v['state']): i for i, v in enumerate(automaton)}
    reached = [0 for i in automaton]
    reached[state2index[str(start_state)]] = 1
    DFS(automaton, start_state, state2index, reached)
    print(len(automaton), sum(reached))
    print(sum(reached), file=f)
    new_auto = []
    for i, vertex in enumerate(automaton):
        if reached[i]:
            new_auto.append(vertex)
    new_state2index = {str(v['state']): i for i, v in enumerate(new_auto)}
    for i, vertex in enumerate(new_auto):
        t0 = new_state2index[str(vertex['transitions'][0])]
        t1 = new_state2index[str(vertex['transitions'][1])]
        unsafe = not vertex['safe']
        print(f"{t0} {t1} {int(unsafe)}", file=f)

def diagnose_interactive(automaton, start_state=None):
    if start_state is None:
        start_state = (0, 0, 0)

    find_vertex = lambda state: [v for v in automaton if v['state'] == state][0]

    now_vertex = find_vertex(start_state)

    while True:
        print(now_vertex['state'])

        choice = int(input())
        assert(choice == 0 or choice == 1)

        now_vertex = find_vertex(now_vertex['transitions'][choice])

def main ():
    assert(len(sys.argv) == 3)

    with open(sys.argv[1]) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    output_file = sys.argv[2]
    if os.path.isfile(output_file):
        while True:
            yn = input(f"{output_file} already exists, overwrite? (y/n)\n")
            if yn == 'n':
                exit()
            elif yn == 'y':
                break

    automaton = generate_automaton(
        config['x_min'], config['x_max'], config['x_interval'],
        config['v_min'], config['v_max'], config['v_interval'],
        config['a'], config['dx_atk'])

    with open(output_file, 'w') as f:
        export_automaton(automaton, f)

    print(f"number of vertices: {len(automaton)}")
    trans_num = 0
    for i in automaton:
        trans_num+=len(i['transitions'])
    print("number of transitions:", trans_num)

    # if input(f"diagnose interactively? (y/n)\n") == 'y':
    #     diagnose_interactive(automaton)

if __name__ == '__main__':
    main()
