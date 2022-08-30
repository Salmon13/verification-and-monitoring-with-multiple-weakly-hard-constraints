import numpy as np

from sortedcontainers.sortedset import SortedSet

class MySortedSet(SortedSet):
  '''
  not used.
  '''
  def __hash__(self):
    return hash( repr(self) )

class Pair(object):
  '''
  stores an (m, k) pair
  '''
  def __init__(self, m, k):
    assert isinstance(m, int) and isinstance(k, int)
    self.m = m
    self.k = k
  
  def __repr__(self):
    return '({}, {})'.format(self.m, self.k)

  def __lt__(self, other):
    return (self.k, self.m) < (other.k, other.m)

  def __eq__(self, other):
    return self.m == other.m and self.k == other.k

  def __hash__(self):
    return hash( repr(self) )

class BaseGridVerifier(object):
  '''
  Parent class for monotonic verifier & proposed verifier
  '''
  def __init__(self, k_bar):
    self.k_bar = k_bar

  def compute_cost_matrix(self):
    '''
    computes the estimated cost matrix
    '''
    factorials = [1]
    for i in range(1, self.k_bar):
      factorials.append( factorials[-1] * i )

    cost_matrix = [ [1. for m in range(self.k_bar + 1)] for k in range(self.k_bar + 1) ]
    for k in range(2, self.k_bar + 1):
      for m in range(1, k):
        cost_matrix[m][k] = cost_matrix[m-1][k] + factorials[k-1] / (factorials[m] * factorials[k-1-m])

    return np.array(cost_matrix)

if __name__ == '__main__':
  bv = BaseGridVerifier(10)
  bv.compute_cost_matrix()

  # for i, cm in enumerate(bv.cost_matrix):
  #   print (i, ':', cm)

  print ( np.flip(bv.cost_matrix[1:, 1:].T, axis=0) )
