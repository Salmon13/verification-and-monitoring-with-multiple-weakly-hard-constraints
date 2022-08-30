import random, pickle
import numpy as np
from time import time

from .mock_single_verifier import MockSingleVerifier, BoundSingleVerifier
from .monotonic_verifier import MonotonicVerifier
from .probe_verifier import ProbeVerifier

if __name__ == '__main__':
  # to store the results (estimated total cost) & additional overhead
  res_per_k_bar, ovh_per_k_bar = [], []
  std_per_k_bar = []

  pv_schc_trace, pv_schb_trace = [], []
  mv_trace = []

  for k_bar in [7, 10, 15, 20, 25]:
    mv_costs, pv_scha_costs, pv_schb_costs, pv_schc_costs = [], [], [], []
    mv_overhead, pv_scha_overhead, pv_schb_overhead, pv_schc_overhead = [], [], [], []

    boundaries = pickle.load( open('./all_boundaries/bounds_k{}.pkl'.format(k_bar), 'rb') )
    if len(boundaries) > 1000:
      boundaries = random.sample( boundaries, 1000 )

    for i, b in enumerate(boundaries):
      print ('idx:', i)
      bound_single = BoundSingleVerifier(k_bar, b)

      pva = ProbeVerifier(k_bar, single_verifier=bound_single)
      pv = ProbeVerifier(k_bar, single_verifier=bound_single)
      pv2 = ProbeVerifier(k_bar, single_verifier=bound_single)
      mv = MonotonicVerifier(k_bar, single_verifier=bound_single)

      start_t = time()
      # this is not used (scheme A in the notes)
      pvat, pvac = pva.verify_all(print_process=False, use_cost_matrix=True)
      pv_scha_overhead.append( 1000 * (time() - start_t) )

      start_t = time()
      # this is not used (scheme B in the notes)
      pvt, pvc = pv.verify_all(print_process=False, use_cost_matrix=False)
      pv_schb_overhead.append( 1000 * (time() - start_t) )

      start_t = time()
      # this is the proposed approach
      pvt2, pvc2 = pv2.verify_all(print_process=False, use_cost_matrix=False, use_interpol_prob=False, account_others=False)
      pv_schc_overhead.append( 1000 * (time() - start_t) )

      start_t = time()
      # baseline: monotonic approach
      mvt, mvc = mv.verify_all(print_process=False)
      mv_overhead.append( 1000 * (time() - start_t) )
      
      print ('  --> probe verifier cost (A):', pvac)
      print ('  --> probe verifier cost (B):', pvc)
      print ('  --> probe verifier cost (min):', pvc2) # this is the proposed approach
      print ('  --> monotonic verifier cost:', mvc)

      pv_scha_costs.append( pvac )
      pv_schb_costs.append( pvc )
      pv_schc_costs.append( pvc2 )
      mv_costs.append( mvc )

      # record (safe/unsafe boundary, total estimated cost, verification path)
      pv_schb_trace.append([b, pvc, pvt])
      pv_schc_trace.append([b, pvc2, pvt2])
      mv_trace.append([b, mvc, mvt])

    res_per_k_bar.append( [round(np.mean(pv_scha_costs), 2), round(np.mean(pv_schb_costs), 2), round(np.mean(pv_schc_costs), 2), round(np.mean(mv_costs), 2)] )
    std_per_k_bar.append( [round(np.std(pv_scha_costs), 2), round(np.std(pv_schb_costs), 2), round(np.std(pv_schc_costs), 2), round(np.std(mv_costs), 2)] )
    ovh_per_k_bar.append( [round(np.mean(pv_scha_overhead), 2), round(np.mean(pv_schb_overhead), 2), round(np.mean(pv_schc_overhead), 2), round(np.mean(mv_overhead), 2)] )

  for i, k_bar in enumerate([7, 10, 15, 20, 25]):
    print ('========== Final Report (k = {:2d}) =========='.format(k_bar))
    print ('probe verifier (A): \tmean={} \tstd={} \tmean_effort={}'.format( 
      res_per_k_bar[i][0], std_per_k_bar[i][0], ovh_per_k_bar[i][0]
    ))
    print ('probe verifier (B): \tmean={} \tstd={} \tmean_effort={}'.format( 
      res_per_k_bar[i][1], std_per_k_bar[i][1], ovh_per_k_bar[i][1]
    ))
    print ('probe verifier (min): \tmean={} \tstd={} \tmean_effort={}'.format( 
      res_per_k_bar[i][2], std_per_k_bar[i][2], ovh_per_k_bar[i][2]
    ))
    print ('monotonic verifier: \tmean={} \tstd={} \tmean_effort={}'.format( 
      res_per_k_bar[i][3], std_per_k_bar[i][3], ovh_per_k_bar[i][3]
    ))

    pickle.dump(pv_schb_trace, open('results/probe_noweight_k7_res.pkl', 'wb'))
    # save the verification path
    pickle.dump(pv_schc_trace, open('results/probe_greed_k7_res.pkl', 'wb'))

    # np.save('results/probe_weight_k{}_costs'.format(k_bar), pv_schb_costs)
    # np.save('results/monotonic_k{}_costs'.format(k_bar), mv_costs)

    # np.save('results/probe_weight_k{}_ovh'.format(k_bar), pv_schb_overhead)
    # np.save('results/monotonic_k{}_ovh'.format(k_bar), mv_overhead)
