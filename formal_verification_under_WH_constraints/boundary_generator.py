from .probe_verifier import ProbeVerifier
from .containers import Pair
import pickle, random
from copy import deepcopy

class BoundaryGenerator(object):
  '''
  For generating all possible (theorem-conforming) safety grid unsafe/safe boundaries given upper bound K (k_bar).
  '''
  def __init__(self, k_bar):
    self.k_bar = k_bar

    self.S = dict()
    ProbeVerifier.get_all_safe_implications(self, perform_check=False)
    self.U = dict()
    ProbeVerifier.get_all_unsafe_implications(self, perform_check=False)

    self.compute_pair_max_safe_m()
    self.compute_pair_min_unsafe_m()

  def compute_pair_max_safe_m(self):
    self.M_max_safe = dict()

    for p_mk in self.S.keys():
      record = [0 for k in range(self.k_bar + 1)]

      for impl in self.S[p_mk]:
        if impl.m > record[impl.k]:
          record[impl.k] = impl.m

      self.M_max_safe[p_mk] = record

    return

  def compute_pair_min_unsafe_m(self):
    self.M_min_unsafe = dict()

    for p_mk in self.U.keys():
      record = [k for k in range(self.k_bar + 1)]

      for impl in self.U[p_mk]:
        if impl.m < record[impl.k]:
          record[impl.k] = impl.m

      self.M_min_unsafe[p_mk] = record

    return

  def _get_safe_region_c(self, p_mk):
    '''
    Region c: 
      * (k' / m') >= (p_mk.k / p_mk.m)
      * m' <= (0.5 * p_mk.m)
    '''

    return ProbeVerifier._get_safe_region_c(self, p_mk)

  def _get_unsafe_multiples(self, p_mk):
    '''
    By Theorem 3
     * For any int(x) >= 2, if (m, k) is unsafe, then (xm, xk) is unsafe
    '''
    return ProbeVerifier._get_unsafe_multiples(self, p_mk)

  def _compute_safe_impl(self, p_mk, save_intermediate=True):
    return ProbeVerifier._compute_safe_impl(self, p_mk, save_intermediate=save_intermediate)
  
  def _compute_unsafe_impl(self, p_mk, save_intermediate=True):
    return ProbeVerifier._compute_unsafe_impl(self, p_mk, save_intermediate=save_intermediate)

  def compute_all_legal_boundaries(self):
    self.bounds = []

    self._bound_recursion_helper(Pair(0, 2), [0 for k in range(self.k_bar + 1)])
    self._bound_recursion_helper(Pair(1, 2), [0 for k in range(self.k_bar + 1)])

    return self.bounds

  def get_random_legal_boundary(self):
    '''
    Use this when K is too big, such that generating all boundaries isn't feasible
    '''
    while True:
      record = [0, 0]
      rand_proportion = random.random()
      rand_m = [0] + [random.choices([0, 1], k=1, weights=[1 - rand_proportion, rand_proportion])[0] for k in range(1, self.k_bar)]
      success = True

      for cur_k in range(2, self.k_bar + 1):
        new_m = record[-1] + rand_m[cur_k - 1]
        for k, record_m in enumerate(record):
          if k < 2:
            continue
          if record_m < self.M_max_safe[ Pair(new_m, cur_k) ][k]:
            success = False
            break

        for k, record_m in enumerate(record):
          if k < 2:
            continue
          if new_m + 1 > self.M_min_unsafe[ Pair(record_m + 1, k) ][cur_k]:
            success = False
            break

        if not success:
          break
        else:
          record.append( new_m )

      if len(record) == self.k_bar + 1:
        # print (rand_proportion)
        return record     


  def _bound_recursion_helper(self, p_mk, record):
    # perform checks over previously placed (m, k)
    for k, record_m in enumerate(record):
      if k >= p_mk.k:
        break
      if k < 2:
        continue
      if record_m < self.M_max_safe[ p_mk ][k]:
        # print ('safety violated:', (record_m, k), (self.M_max_safe[ p_mk ][k], k))
        return

    for k, record_m in enumerate(record):
      if k >= p_mk.k:
        break
      if k < 2:
        continue
      if p_mk.m + 1 > self.M_min_unsafe[ Pair(record_m + 1, k) ][p_mk.k]:
        # print ('unsafety violated:', (p_mk.m + 1, p_mk.k), (self.M_min_unsafe[ Pair(record_m + 1, k) ][p_mk.k], p_mk.k))
        return

    record[p_mk.k] = p_mk.m
    if p_mk.k == self.k_bar:
      self.bounds.append( deepcopy(record) )
      # print (len(self.bounds))
      # print (record)
      return

    self._bound_recursion_helper(Pair(p_mk.m, p_mk.k+1), record)
    self._bound_recursion_helper(Pair(p_mk.m+1, p_mk.k+1), record)

    return

if __name__ == '__main__':
  bg = BoundaryGenerator(30)
  
  # for k in sorted(bg.M_max_safe.keys(), key=lambda x: (x.k, x.m)):
  #   print (k, ':', bg.M_max_safe[k])

  # for k in sorted(bg.M_min_unsafe.keys(), key=lambda x: (x.k, x.m)):
  #   print (k, ':', bg.M_min_unsafe[k])

  # bounds = bg.compute_all_legal_boundaries()
  # print (len(bounds[0]))
  # print (bounds)

  # pickle.dump(bounds, open('./all_boundaries/bounds_k8.pkl', 'wb'))

  print (bg.get_random_legal_boundary())
