import os
import random
import math
import yaml
import sys

def generate_automation(config):
    '''
    Output:
        automation (list(dict{state, transition})):
            state (tuple(int, int, int)): (x, v, a)
            transitions (dict(string: list(tuple(int, int, int)))):
                map signal to list of transitioned states
    '''
    default_unsafe_state = (-1,-1,-1,-1,-1,-1)
    default_safe_state = (-2,-2,-2,-2,-2,-2)
    automation = [{
        'state': default_unsafe_state,
        'transitions': [default_unsafe_state, default_unsafe_state, default_unsafe_state, default_unsafe_state],
        'safe': False
    },{
        'state': default_safe_state,
        'transitions': [default_safe_state, default_safe_state, default_safe_state, default_safe_state],
        'safe': True
    }]
    reached = {default_unsafe_state:1, default_safe_state:1}

    DFS(automation, reached, config, default_unsafe_state, default_safe_state)

    return automation

def calculate_transitions(state, x_min, x_max, v_max1, v_max2,  default_unsafe_state, default_safe_state):
    transitions = []
    x1, v1, a1, x2, v2, a2 = state

    # 0 : sum 
    # - 1, 1 : sum + 1
    clamp_v1 = lambda v: min(max(v, 10), v_max1)
    clamp_v2 = lambda v: min(max(v, 10), v_max2)

    for signal in [0, 1, 2, 3]: # 00, 01, 10, 11: lead signal, follow signal
        v1_nxt = clamp_v1(v1+a1)
        x1_nxt = x1 + v1 + a1//2

        x2_nxt = x2 + v2 + a2//2
        v2_nxt = clamp_v2(v2 + a2)

        if signal % 2 == 1:   # leading car misses message: 0 or 1
            a1_nxt = 2
        elif x1 - x2 < 10:
            a1_nxt = 4
        elif x1 - x2 > 20:
            a1_nxt = 0
        else:
            a1_nxt = 2

        if signal // 2 == 1: # following car misses message: 0 or 2
            a2_nxt = 0
        elif x1 - x2 < 10:
            a2_nxt = -4
        elif x1 - x2 > 20:
            a2_nxt = 4
        else:
            a2_nxt = 2


        if x1 <= x_max and x2 <= x_max and x1-x2 > 4 and x1-x2 < 30:
            transition = (x1_nxt, v1_nxt, a1_nxt, x2_nxt, v2_nxt, a2_nxt)
        elif x1 > x_max or x2 > x_max:
            transition = default_safe_state
        else:
            transition = default_unsafe_state

        transitions.append(transition)

    return tuple(transitions)

def DFS(automation, reached, config, default_unsafe_state, default_safe_state):
    start_state = (config['x_start_lead'], config['v_start_lead'], config['a_start_lead'],
                    config['x_start_follow'], config['v_start_follow'], config['a_start_follow'])
    l = [start_state]
    i = 0
    while len(l) != 0:
        s = l.pop(len(l)-1)
        # print(s)
        if s in reached:
            continue
        reached[s] = 1
        #print(automation[state2index[str(state)]])
        transitions = calculate_transitions(s,
                                            config['x_min'], config['x_max'], 
                                            config['v_max_lead'], config['v_max_follow'],
                                            default_unsafe_state, default_safe_state)
        vertex = {
            'state': s,
            'transitions': transitions,
            'safe': True
        }
        automation.append(vertex)
        # print(len(automation), end='\r')
        for tran in transitions:
            i = i + 1
            l.append(tran)
    return

def export_automation(automation, f, start_state):
    # move start state to front
    start_index = [i for i, v in enumerate(automation) if v['state'] == start_state][0]
    automation.insert(0, automation.pop(start_index))
    print(len(automation), file=f)
    # construct dict: state -> index
    state2index = {str(v['state']): i for i, v in enumerate(automation)}
    for i, vertex in enumerate(automation):
        # print(i, end='\r')
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

    automation = generate_automation(config)

    with open(output_file, 'w') as f:
        export_automation(automation, f, start_state=\
            (
                config['x_start_lead'], config['v_start_lead'], config['a_start_lead'],
                config['x_start_follow'], config['v_start_follow'], config['a_start_follow']
            )
        )

    print(f"number of vertices: {len(automation)}")
    trans_num = 0
    for i in automation:
        trans_num+=len(i['transitions'])
    print("number of transitions:", trans_num)

if __name__ == '__main__':
    main()
