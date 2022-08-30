import pickle
import numpy as np
from time import time
import sys

from formal_verification_under_WH_constraints.mock_single_verifier import BoundSingleVerifier
from formal_verification_under_WH_constraints.monotonic_verifier import MonotonicVerifier
from formal_verification_under_WH_constraints.probe_verifier import ProbeVerifier
from formal_verification_under_WH_constraints.shortcut_verifier import ShortcutVerifier
from formal_verification_under_WH_constraints.lfs_heuristic_verifier import LFSHeuristicVerifier
from formal_verification_under_WH_constraints.optimal_verifier import OptimalVerifier

def evaluate_pv_and_mv(k_bar, boundary, cost_matrix):

    single_v = BoundSingleVerifier(k_bar, boundary)
    pv = ProbeVerifier(k_bar, single_v, cost_matrix)
    mv = MonotonicVerifier(k_bar, single_v, cost_matrix)
    sv = ShortcutVerifier(k_bar, single_v, cost_matrix)
    lv = LFSHeuristicVerifier(k_bar, single_v, cost_matrix)
    ov = OptimalVerifier(k_bar, single_v, cost_matrix)

    start_t = time()
    pv_trace, pv_cost = pv.verify_all(print_process=False,
                                      use_cost_matrix=False,
                                      use_interpol_prob=False,
                                      account_others=False)
    pv_time = 1000 * (time() - start_t)

    start_t = time()
    mv_trace, mv_cost = mv.verify_all(print_process=False)
    mv_time = 1000 * (time() - start_t)

    start_t = time()
    sv_trace, sv_cost = sv.verify_all()
    sv_time = 1000 * (time() - start_t)

    start_t = time()
    lv_trace, lv_cost = lv.verify_all()
    lv_time = 1000 * (time() - start_t)

    start_t = time()
    ov_trace, ov_cost = ov.verify_all(boundary)
    ov_time = 1000 * (time() - start_t)

    # return pv_time, mv_time
    print('Traces:')
    # print('\tprobe', pv_trace)
    print('\tMONO:', mv_trace)
    print('\tMONO-DUB:', sv_trace)
    print('\tLCF:', lv_trace)
    print('\tOPT:', ov_trace)
    return pv_cost, mv_cost, sv_cost, lv_cost, ov_cost

def main():
    k_bar = int(sys.argv[1])
    boundary_csv = sys.argv[2]
    cost_matrix_csv = sys.argv[3]

    boundary = np.genfromtxt(boundary_csv, delimiter=',')
    cost_matrix = np.genfromtxt(cost_matrix_csv, delimiter=',')

    pv_time, mv_time, sv_time, lv_time, ov_time = evaluate_pv_and_mv(k_bar, boundary, cost_matrix)
    print('Runtimes:')
    print('\tBF:', np.sum(cost_matrix), 'sec')
    # print('\tprobe', pv_time)
    print('\tMONO:', mv_time, 'sec')
    print('\tMONO-DUB', sv_time, 'sec')
    print('\tLCF:', lv_time, 'sec')
    print('\tOPT:', ov_time, 'sec')

if __name__ == '__main__':
    main()
