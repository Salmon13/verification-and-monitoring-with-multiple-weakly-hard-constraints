import numpy as np
from formal_verification_under_WH_constraints.containers import Pair, BaseGridVerifier

class ShortcutVerifier(BaseGridVerifier):
    def __init__(self, k_bar, single_verifier, cost_matrix=None):
        super().__init__(k_bar)
        self.single_verifier = single_verifier
        if cost_matrix is None:
            self.compute_cost_matrix()
        else:
            self.cost_matrix = cost_matrix

    def verify_all(self):
        dynamic_boundary = np.arange(self.k_bar + 1)
        # defined as the minimum m that is unsafe

        verification_trace = []
        verification_cost = 0

        m, k = 0, 1

        while k <= self.k_bar:
            while m + 1 < dynamic_boundary[k]:
                # eval
                verification_trace.append(Pair(m + 1, k))
                verification_cost += self.cost_matrix[m + 1, k]
                satisfied = self.single_verifier.verify(Pair(m + 1, k))

                if not satisfied:
                    # update boundary by thm 3 and thm 4
                    x = 1 # start from 1 to save dynamic_boundary[k] = m + 1
                    while x * k <= self.k_bar:
                        dynamic_boundary[x * k] = min(x * (m + 1),
                                                      dynamic_boundary[x * k])
                        x += 1
                    if k + 1 <= self.k_bar:
                        dynamic_boundary[k + 1] = min(m + 2,
                                                      dynamic_boundary[k + 1])
                    break
                m += 1
            k += 1

        # print(dynamic_boundary)
        return verification_trace, verification_cost
