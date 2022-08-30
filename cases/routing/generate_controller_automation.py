import os
import random
import math
import yaml
import sys

def generate_automaton(s1_min, s1_max, s2_min, s2_max, c1_max, c2_max):
    '''
    Output:
        automaton (list(dict{state, transition})):
            state (tuple(int, int, int)): (x, v, a)
            transitions (dict(string: list(tuple(int, int, int)))):
                map signal to list of transitioned states
    '''
    default_unsafe_state = (None, None, None, None, None, None, None)
    automaton = [{
        'state': default_unsafe_state,
        'transitions': [default_unsafe_state, default_unsafe_state],
        'safe': False
    }]
    reached = {default_unsafe_state:1}
    start_state = (-8, 1, 0, -16, 1, 0, 1)
    DFS(automaton, start_state, reached, s1_min, s1_max, s2_min, s2_max, c1_max, c2_max, default_unsafe_state)

    return automaton

def calculate_transitions(s1, st1, c1, s2, st2, c2, flag, s1_min, s1_max, s2_min, s2_max, c1_max, c2_max, default_unsafe_state):
    '''
    Input:
        state (tuple(int, int, int)): (x, v, a)
    Output:
        transitions (tuple(tuple(int, int, int), tuple(int, int, int))):
            list of transitioned states for 0 and 1
    '''
    transitions = []

    # 0 : sum - 1, 1 : sum + 1
    for signal in [0, 1]:
        buf = [-1, 1][signal]
        if flag == 1 and st1 and s1_min <= s1 + buf <= s1_max:
            s1_nxt = s1 + buf
        elif flag == 2:
            s1_nxt = s1_min
        else:
            s1_nxt = s1
        if flag == 1 and s1 + buf > 0:
            st1_nxt = 0
        elif flag == 2 and c1 == c1_max:
            st1_nxt = 1
        else:
            st1_nxt = st1
        if flag == 2 and c1 < c1_max:
            c1_nxt = c1+1
        elif flag == 1:
            c1_nxt = 0
        else:
            c1_nxt = c1

        if flag == 2 and st2 and s2_min <= s2 + buf <= s2_max:
            s2_nxt = s2 + buf
        elif flag == 1:
            s2_nxt = s2_min
        else:
            s2_nxt = s2
        if flag == 2 and s2 + buf > 0:
            st2_nxt = 0
        elif flag == 1 and c2 == c2_max:
            st2_nxt = 1
        else:
            st2_nxt = st2
        if flag == 1 and c2 < c2_max:
            c2_nxt = c2+1
        elif flag == 2:
            c2_nxt = 0
        else:
            c2_nxt = c2
        
        if flag == 1 and st1 == 0:
            flag_nxt = 2
        elif flag == 2 and st2 == 0:
            flag_nxt = 1
        else:
            flag_nxt = flag

        if st1_nxt == 1 or st2_nxt == 1:
            transition = (s1_nxt, st1_nxt, c1_nxt, s2_nxt, st2_nxt, c2_nxt, flag_nxt)
        else:
            transition = default_unsafe_state

        transitions.append(transition)

    return tuple(transitions)
def DFS(automaton, state, reached, s1_min, s1_max, s2_min, s2_max, c1_max, c2_max, default_unsafe_state):
    l = [state]
    while len(l) != 0:
        s = l.pop(len(l)-1)
        if s in reached:
            continue
        reached[s] = 1
        #print(automaton[state2index[str(state)]])
        transitions = calculate_transitions(s[0], s[1], s[2],
                                        s[3], s[4], s[5], s[6],
                                        s1_min, s1_max,
                                        s2_min, s2_max,
                                        c1_max, c2_max,
                                        default_unsafe_state)
        vertex = {
            'state': s,
            'transitions': transitions,
            'safe': True
        }
        automaton.append(vertex)
        for tran in transitions:
            l.append(tran)
    return
def export_automaton(automaton, f, start_state=None):
    # set start state
    if start_state is None:
        start_state = (-8, 1, 0, -16, 1, 0, 1)
    # move start state to front
    start_index = [i for i, v in enumerate(automaton) 
                   if v['state'] == start_state][0]
    automaton.insert(0, automaton.pop(start_index))
    # construct dict: state -> index
    state2index = {str(v['state']): i for i, v in enumerate(automaton)}

    print(len(automaton), file=f)
    for vertex in automaton:
        t0 = state2index[str(vertex['transitions'][0])]
        t1 = state2index[str(vertex['transitions'][1])]
        unsafe = not vertex['safe']
        print(f"{t0} {t1} {int(unsafe)}", file=f)


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
        config['s1_min'], config['s1_max'], config['s2_min'], 
        config['s2_max'], config['c1_max'], config['c2_max'])

    with open(output_file, 'w') as f:
        export_automaton(automaton, f)

    print(f"number of vertices: {len(automaton)}")
    trans_num = 0
    for i in automaton:
        trans_num+=len(i['transitions'])
    print("number of transitions:", trans_num)
if __name__ == '__main__':
    main()
