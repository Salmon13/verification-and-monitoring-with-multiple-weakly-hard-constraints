from formal_verification_under_WH_constraints.probe_verifier import ProbeVerifier
import utility
from time import time
import numpy as np

class OptimalVerifier(ProbeVerifier):
    def __init__(self, k_bar, single_verifier=None, cost_matrix=None):
        super().__init__(k_bar, single_verifier, cost_matrix)

        self.sub2whole, self.whole2sub = utility.get_implied_cases(k_bar)

    def verify_all(self, boundary):
        self.verification_trace = []
        self.verification_cost = 0.
    
        implied = [[(i,j) for j in range(self.cost_matrix.shape[0])] for i in range(self.cost_matrix.shape[0])]
        for i in range(1,self.cost_matrix.shape[0]):
            for j in range(i,self.cost_matrix.shape[0]):
                if implied[i][j] == (i,j):
                    if i <= boundary[j]:
                        for case in self.whole2sub[implied[i][j]]:
                            implied[case[0]][case[1]] = implied[i][j]
                    else:
                        for case in self.sub2whole[implied[i][j]]:
                            implied[case[0]][case[1]] = implied[i][j]
        #print("In optimal path (1,3)", implied[1][3])
        path = {}
        runtime = 0.0
        for i in range(1,self.cost_matrix.shape[0]):
            for j in range(i,self.cost_matrix.shape[0]):
                path[implied[i][j]] = 0
        path = [i for i in path]
        for i in path:
            runtime+=self.cost_matrix[i[0]][i[1]]
        
        self.verification_cost = runtime
        self.verification_trace = path
        return self.verification_trace, self.verification_cost
