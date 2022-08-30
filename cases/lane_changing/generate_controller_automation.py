import os
import random
import math
import yaml
import sys

def generate_automaton(x_min, x_max, v_min, v_max):
    '''
    Output:
        automaton (list(dict{state, transition})):
            state (tuple(int, int, int)): (x, v, a)
            transitions (dict(string: list(tuple(int, int, int)))):
                map signal to list of transitioned states
    '''
    default_unsafe_state = (None, None, None, None, None, None, None)
    default_safe_state = (None, None, None, None, None, None, 0)
    automaton = [{
        'state': default_unsafe_state,
        'transitions': [default_unsafe_state, default_unsafe_state, default_unsafe_state, default_unsafe_state],
        'safe': False
    },{
        'state': default_safe_state,
        'transitions': [default_safe_state, default_safe_state, default_safe_state, default_safe_state],
        'safe': True
    }]
    reached = {default_unsafe_state:1, default_safe_state:1}
    start_state = (0, 0, 1, 1, 1, 1, 0)
    DFS(automaton, start_state, reached, x_min, x_max, v_min, v_max, default_unsafe_state, default_safe_state)

    return automaton

def calculate_transitions(x1, x2, v1, v2, a1, a2, changed, x_min, x_max, v_min, v_max, default_unsafe_state, default_safe_state):
    '''
    Input:
        state (tuple(int, int, int)): (x, v, a)
    Output:
        transitions (tuple(tuple(int, int, int), tuple(int, int, int))):
            list of transitioned states for 0 and 1
    '''
    transitions = []

    # 0 : sum - 1, 1 : sum + 1
    for signal in [0, 1, 2, 3]:
        if v_min <= v1 + a1 <= v_max:
            v1_nxt = v1 + a1
        else:
            v1_nxt = v1
        if v_min <= v2 + a2 <= v_max:
            v2_nxt = v2 + a2
        else:
            v2_nxt = v2
        if x_min <= x1+v1+a1//2 <= x_max:
            x1_nxt = x1+v1+a1//2
        elif x1+v1+a1//2 >=x_max:
            x1_nxt = x_max
        else:
            x1_nxt = x1
        if x_min <= x2+v2+a2//2 <= x_max:
            x2_nxt = x2+v2+a2//2
        elif x2+v2+a2//2:
            x2_nxt = x_max
        else:
            x2_nxt = x2
        if signal%2 == 1:
            a1_nxt = 0
        elif x2 - 2 < x1 < x2 + 2 and v1 == v2:
            a1_nxt = 2
        elif x2 - 2 < x1 < x2 + 2 and v1 > v2:
            a1_nxt = 5
        elif x2 - 2 < x1 < x2 + 2 and v1 < v2:
            a1_nxt = -5
        elif x2 + v2 + a2//2 > x1:
            a1_nxt = -5
        elif x2 + v2 + a2//2 < x1:
            a1_nxt = 5
        else:
            a1_nxt = a1
        if signal//2 == 1:
            a2_nxt = a2
        elif x1 - 2 < x2 < x1 + 2 and v2 == v1:
            a2_nxt = -2
        elif x1 - 2 < x2 < x1 + 2 and v2 > v1:
            a2_nxt = 5
        elif x1 - 2 < x2 < x1 + 2 and v2 < v1:
            a2_nxt = -5
        elif x1 + v1 + a1//2 > x2:
            a2_nxt = -5
        elif x1 + v1 + a1//2 < x2:
            a2_nxt = 5
        else:
            a2_nxt = a2
        if changed == 0 and abs(x1 - x2) > 4:
            changed_nxt = 1
        else:
            changed_nxt = changed
        if x1 == x_max and changed == 0 or x2 == x_max and changed == 0:
            transition = default_unsafe_state
        elif changed:
            transition = default_safe_state
        else:
            transition = (x1_nxt, x2_nxt, v1_nxt, v2_nxt, a1_nxt, a2_nxt, changed_nxt)

        transitions.append(transition)

    return tuple(transitions)
def DFS(automaton, state, reached, x_min, x_max, v_min, v_max, default_unsafe_state, default_safe_state):
    l = [state]
    cnt1, cnt2 = [0], [0]
    max1, max2 = [0], [0]
    min_m = 10**9
    while len(l) != 0:
        s = l.pop(len(l)-1)
        m1 = max1.pop(len(max1)-1)
        m2 = max2.pop(len(max2)-1)
        c1 = cnt1.pop(len(cnt1)-1)
        c2 = cnt2.pop(len(cnt2)-1)
        if s in reached:
            if s == default_unsafe_state:
                min_m = min(max(m1, m2), min_m)
            continue
        reached[s] = 1
        #print(automaton[state2index[str(state)]])
        transitions = calculate_transitions(s[0], s[1], s[2], 
                                            s[3], s[4], s[5], s[6],
                                            x_min, x_max,
                                            v_min, v_max,
                                            default_unsafe_state,
                                            default_safe_state)
        vertex = {
            'state': s,
            'transitions': transitions,
            'safe': True
        }
        automaton.append(vertex)
        for i, tran in enumerate(transitions):
            l.append(tran)
            if i % 2 == 0:
                cnt1.append(0)
                max1.append(m1)
            else:
                cnt1.append(c1+1)
                max1.append(max(m1, c1+1))
            if i // 2 == 0:
                cnt2.append(0)
                max2.append(m2)
            else:
                cnt2.append(c2+1)
                max2.append(max(m2, c2+1))
    #with open("pre_m.txt", 'w') as f:
    #    print(min_m, file = f)
    #print("min_m", min_m)
    return
def export_automaton(automaton, f, start_state=None):
    # set start state
    if start_state is None:
        start_state = (0, 0, 1, 1, 1, 1, 0)
    # move start state to front
    start_index = [i for i, v in enumerate(automaton) if v['state'] == start_state][0]
    automaton.insert(0, automaton.pop(start_index))
    # construct dict: state -> index
    state2index = {str(v['state']): i for i, v in enumerate(automaton)}
    print(len(automaton), file=f)
    for i, vertex in enumerate(automaton):
        t0 = state2index[str(vertex['transitions'][0])]
        t1 = state2index[str(vertex['transitions'][1])]
        t2 = state2index[str(vertex['transitions'][2])]
        t3 = state2index[str(vertex['transitions'][3])]
        unsafe = not vertex['safe']
        print(f"{t0} {t1} {t2} {t3} {int(unsafe)}", file=f)

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
        config['x_min'], config['x_max'], config['v_min'], 
        config['v_max'])

    with open(output_file, 'w') as f:
        export_automaton(automaton, f)

    print(f"number of vertices: {len(automaton)}")
    trans_num = 0
    for i in automaton:
        trans_num+=len(i['transitions'])
    print("number of transitions:", trans_num)
if __name__ == '__main__':
    main()
