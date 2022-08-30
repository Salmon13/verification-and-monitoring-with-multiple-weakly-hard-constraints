import random

from .containers import Pair, BaseGridVerifier
from .mock_single_verifier import MockSingleVerifier

class MonotonicVerifier(BaseGridVerifier):
  '''
  Kai-Chieh's monotonic approach.
  '''
  def __init__(self, k_bar, single_verifier=None, cost_matrix=None):
    super().__init__(k_bar)
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

  def verify_all(self, print_process=True):
    # print ('---------- [ Monotonic Verifier ] ----------')
    self.verification_trace = []
    self.verification_cost = 0.

    cur_m, cur_k = 1, 2
    while cur_k <= self.k_bar and cur_m <= cur_k:
      self.verification_trace.append( Pair(cur_m, cur_k) )
      self.verification_cost += self.cost_matrix[cur_m, cur_k]
      if print_process:
        print ('[verifying ...] --> {} chosen.'.format( Pair(cur_m, cur_k) ))

      # simulated verification, returns immediately
      satisfied = self.single_verifier.verify( Pair(cur_m, cur_k) )

      if satisfied:
        cur_m += 1
      else:
        cur_k += 1

    if print_process:
      print ('Verification completed -- # iterations: {}'.format(len(self.verification_trace)))
      print ('Trace:', self.verification_trace)
      print ('Cost:', self.verification_cost)

    return self.verification_trace, self.verification_cost

if __name__ == "__main__":
  mv = MonotonicVerifier(30)
  mv.verify_all()
