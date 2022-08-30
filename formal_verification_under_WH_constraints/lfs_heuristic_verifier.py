from formal_verification_under_WH_constraints.probe_verifier import ProbeVerifier

class LFSHeuristicVerifier(ProbeVerifier):
    def __init__(self, k_bar, single_verifier=None, cost_matrix=None):
        super().__init__(k_bar, single_verifier, cost_matrix)

        self.estimated_cost_matrix = self.compute_cost_matrix()

    def verify_all(self):
        self.verification_trace = []
        self.verification_cost = 0.
    
        while self.V:
      
            best_gain, best_p_mk = float('-inf'), None

            for p_mk in self.V:
                W_s = self.V.intersection( self.S[p_mk] )
                W_u = self.V.intersection( self.U[p_mk] )

                # different from original
                g = -self.estimated_cost_matrix[p_mk.m, p_mk.k]

                if g > best_gain:
                    best_gain, best_p_mk = g, p_mk

            self.verification_trace.append(best_p_mk)
            self.verification_cost += self.cost_matrix[best_p_mk.m, best_p_mk.k]
      
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

        assert not self.safe_mks.intersection( self.unsafe_mks )
        return self.verification_trace, self.verification_cost
