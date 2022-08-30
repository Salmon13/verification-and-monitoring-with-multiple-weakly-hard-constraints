from .containers import Pair

class MockSingleVerifier(object):
  '''
  Only models safe/unsafe bounds according to k/m ratios.
  '''
  def __init__(self, slope):
    self.slope = slope

  def verify(self, p_mk):
    return p_mk.k / p_mk.m >= self.slope

class BoundSingleVerifier(object):
  '''
  Takes in a pre-computed safe/unsafe boundary.
  '''
  def __init__(self, k_bar, bound):
    assert len(bound) == k_bar + 1
    self.k_bar = k_bar
    self.bound = bound

  def verify(self, p_mk):
    return p_mk.m <= self.bound[p_mk.k]
