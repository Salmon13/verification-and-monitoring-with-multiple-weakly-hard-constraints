import os
import numpy as np
from math import ceil
from .containers import Pair, BaseGridVerifier
from .mock_single_verifier import MockSingleVerifier
import random

class ProbeVerifier(BaseGridVerifier):
  '''
  The proposed appraoch.
  '''
  def __init__(self, k_bar, single_verifier=None, cost_matrix=None):
    super().__init__(k_bar)

    self.V = self.get_all_mks_to_check()

    self.S = dict()
    self.get_all_safe_implications()
    self.U = dict()
    self.get_all_unsafe_implications()

    if cost_matrix is None:
        self.cost_matrix = self.compute_cost_matrix()
    else:
        self.cost_matrix = cost_matrix

    self.m_upper_k = [k for k in range(self.k_bar + 1)]
    self.m_lower_k = [0 for k in range(self.k_bar + 1)]

    if not single_verifier:
      self.single_verifier = MockSingleVerifier( random.uniform(1.05, 5) )
    else:
      self.single_verifier = single_verifier

    self.unsafe_mks = set([Pair(k, k) for k in range(2, self.k_bar + 1)])
    self.safe_mks = set([Pair(0, k) for k in range(2, self.k_bar + 1)])

  def verify_all(self, use_interpol_prob=True, use_cost_matrix=True, print_process=True, account_others=True):
    self.verification_trace = []
    self.verification_cost = 0.
    # print ('---------- [ Probe Verifier ] ----------')

    while self.V:

      best_gain, best_p_mk = float('-inf'), None

      for p_mk in self.V:
        W_s = self.V.intersection( self.S[p_mk] )
        W_u = self.V.intersection( self.U[p_mk] )
        if use_cost_matrix:
          g_s = np.sum( np.multiply(self.cost_matrix, self.get_grid_mask(W_s)) )
          g_u = np.sum( np.multiply(self.cost_matrix, self.get_grid_mask(W_u)) )
        elif account_others:
          g_s = len(W_s)
          g_u = len(W_u)
        else:
          g_s, g_u = 0, 0

        if use_interpol_prob:
          m_upper, m_lower = self.m_upper_k[ p_mk.k ], self.m_lower_k[ p_mk.k ]
          m_range = m_upper - m_lower
          g = (m_upper - p_mk.m) / m_range * g_s + \
              (p_mk.m - m_lower) / m_range * g_u - \
              self.cost_matrix[p_mk.m, p_mk.k]
        else:
          g = 0.5 * g_s + 0.5 * g_u - self.cost_matrix[p_mk.m, p_mk.k]

        if g > best_gain:
          # print ('  -- [current best] {}'.format(p_mk) )
          # print (self.get_grid_mask(W_s))
          # print (self.get_grid_mask(W_u))
          # print ('  -- expected_gain:', g)
          best_gain, best_p_mk = g, p_mk

      self.verification_trace.append(best_p_mk)
      self.verification_cost += self.cost_matrix[best_p_mk.m, best_p_mk.k]
      if print_process:
        print ('[verifying ...] --> {} chosen.'.format( best_p_mk ))

      satisfied = self.single_verifier.verify( best_p_mk )
      V_prime = self.V

      if satisfied:
        self.safe_mks |= self.S[ best_p_mk ]
        self.V = self.V.difference( self.S[ best_p_mk ] )
        X = V_prime.difference( self.V )
        for p_mk in X:
          if p_mk.m > self.m_lower_k[ p_mk.k ]:
            self.m_lower_k[ p_mk.k ] = p_mk.m

      else:
        self.unsafe_mks |= self.U[ best_p_mk ]
        self.V = self.V.difference( self.U[ best_p_mk ] )
        X = V_prime.difference( self.V )
        for p_mk in X:
          if p_mk.m < self.m_upper_k[ p_mk.k ]:
            self.m_upper_k[ p_mk.k ] = p_mk.m

    if print_process:
      print ('Verification completed -- # iterations: {}'.format(len(self.verification_trace)))
      print ('Trace:', self.verification_trace)
      print ('Cost:', self.verification_cost)

    assert not self.safe_mks.intersection( self.unsafe_mks )
    return self.verification_trace, self.verification_cost

  def get_grid_mask(self, pairs_set):
    indices = [(p.m, p.k) for p in pairs_set]
    rows, cols = zip( *indices )
    grid_mask = np.zeros( (self.k_bar + 1, self.k_bar + 1) )
    grid_mask[rows, cols] = 1.

    return grid_mask

  def get_all_mks_to_check(self):
    V = set()

    for k in range(2, self.k_bar + 1):
      for m in range(1, k):
        V.add( Pair(m, k) )

    return V

  def get_all_safe_implications(self, perform_check=True):
    '''
    computes the safety regions in the note
    '''
    # initialize S(0, k)
    init_set = []
    for k in range(self.k_bar, 1, -1):
      init_set.append( Pair(0, k) )
      self.S[ Pair(0, k) ] = set(init_set)

    # compute every S(m, k)
    for k in range(self.k_bar, 1, -1):
      for m in range(1, k):
        if Pair(m, k) not in self.S:
          self.S[ Pair(m, k) ] = self._compute_safe_impl(Pair(m, k), save_intermediate=False)

        if perform_check:
          self._check_safe_impl_legality(Pair(m, k))

    return

  def get_all_unsafe_implications(self, perform_check=True):
    '''
    computes the unsafety regions in the note
    '''
    # initialize U(k, k)
    init_set = set([Pair(k, k) for k in range(2, self.k_bar + 1)])
    for k in range(2, self.k_bar + 1):
      self.U[ Pair(k, k) ] = init_set

    # compute every U(m, k)
    for k in range(self.k_bar, 1, -1):
      for m in range(k - 1, 0, -1):
        if Pair(m, k) not in self.U:
          self.U[ Pair(m, k) ] = self._compute_unsafe_impl(Pair(m, k), save_intermediate=False)

        if perform_check:
          self._check_unsafe_impl_legality(Pair(m, k))

  def _get_safe_region_c(self, p_mk):
    '''
    Region c:
      * (k' / m') >= (p_mk.k / p_mk.m)
      * m' <= (0.5 * p_mk.m)
    '''

    desc_k = p_mk.k - (p_mk.m - p_mk.m // 2)
    region_c_mks = []

    for m in range(p_mk.m // 2, 0, -1):
      while (desc_k - 1) / m >= p_mk.k / p_mk.m and desc_k > 2:
        desc_k -= 1
      region_c_mks.append( Pair(m, desc_k) )

    # print (p_mk, ':', region_c_mks)
    return region_c_mks

  def _get_unsafe_multiples(self, p_mk):
    '''
    By Theorem 3
     * For any int(x) >= 2, if (m, k) is unsafe, then (xm, xk) is unsafe
    '''

    mults = []
    mult_upper_bound = self.k_bar // p_mk.m

    for x in range(2, mult_upper_bound + 1):
      if x * p_mk.k < self.k_bar:
        mults.append( Pair(x * p_mk.m, x * p_mk.k) )
      elif self.k_bar > (x-1) * p_mk.k + p_mk.m:
        mults.append( Pair(x * p_mk.m, self.k_bar) )
        break
      else:
        break

    # print (p_mk, ':', mults)
    return mults

  def _compute_safe_impl(self, p_mk, save_intermediate=True):
    if p_mk in self.S:
      return self.S[ p_mk ]

    impl_set = set([p_mk])
    # handle Region a & b
    if p_mk.k < self.k_bar:
      impl_set |= self._compute_safe_impl(Pair(p_mk.m, p_mk.k + 1))
    if p_mk.m > 0:
      impl_set |= self._compute_safe_impl(Pair(p_mk.m - 1, p_mk.k))
    if p_mk.k > 2 and p_mk.m > 0:
      impl_set |= self._compute_safe_impl(Pair(p_mk.m - 1, p_mk.k - 1))

    # handle Region c
    for p_c in self._get_safe_region_c(p_mk):
      impl_set |= self._compute_safe_impl(p_c)

    if save_intermediate:
      self.S[ p_mk ] = impl_set

    return impl_set

  def _compute_unsafe_impl(self, p_mk, save_intermediate=True):
    if p_mk in self.U:
      return self.U[ p_mk ]

    impl_set = set([p_mk])
    # handle adjacent (m, k)'s
    if p_mk.k > 2:
      impl_set |= self._compute_unsafe_impl(Pair(p_mk.m, p_mk.k - 1))
    if p_mk.m < p_mk.k - 1:
      impl_set |= self._compute_unsafe_impl(Pair(p_mk.m + 1, p_mk.k))
    if p_mk.k < self.k_bar:
      impl_set |= self._compute_unsafe_impl(Pair(p_mk.m + 1, p_mk.k + 1))

    # handle multiples (xm, xk)
    p_mults = self._get_unsafe_multiples(p_mk)
    for p_m in p_mults:
      impl_set |= self._compute_unsafe_impl(p_m)

    if save_intermediate:
      self.U[ p_mk ] = impl_set

    return impl_set

  def _check_safe_impl_legality(self, p_mk):
    if p_mk in self.S:
      for x in range(0, p_mk.m):
        m = p_mk.m - x
        for k in range(p_mk.k - x, self.k_bar + 1):
          assert Pair(m, k) in self.S[ p_mk ], '{} should be in S({})'.format(Pair(m, k), p_mk)

      for m in range(1, p_mk.m // 2 + 1):
        k_low = int( ceil(m * (p_mk.k / p_mk.m)) )
        k_high = p_mk.k - (p_mk.m - m)
        for k in range(k_low, k_high):
          assert Pair(m, k) in self.S[ p_mk ], '{} should be in S({})'.format(Pair(m, k), p_mk)

    return

  def _check_unsafe_impl_legality(self, p_mk):
    k_high = p_mk.k
    for m in range(p_mk.m, self.k_bar + 1):
      if k_high < self.k_bar and not m % p_mk.m:
        k_high = min(self.k_bar, p_mk.k * (m // p_mk.m))

      for k in range(k_high, max(m - 1, 1), -1):
        assert Pair(m, k) in self.U[ p_mk ], '{} should be in U({})'.format(Pair(m, k), p_mk)

      if k_high < self.k_bar:
        k_high += 1

    return

if __name__ == '__main__':
  ## for code testing only
  pv = ProbeVerifier(20, single_verifier=MockSingleVerifier(3.3))

  # print ( sorted(pv.V, key=lambda x: (x.k, x.m)) )

  # for p_mk in sorted(pv.U.keys(), key=lambda x: (x.k, x.m)):
  #   print (p_mk)
  #   print ('==================================================================')
  #   print ( sorted(pv.U[ p_mk ], key=lambda x: (x.k, x.m)) )
  #   print ('==================================================================')

  # trace, cost = pv.verify_all(use_cost_matrix=True)
  # print (pv.m_lower_k)
  # print (pv.m_upper_k)

  ## verify with the proposed approach
  trace, cost = pv.verify_all(
    print_process=False,
    use_cost_matrix=False,
    use_interpol_prob=False,
    account_others=False
  )
