#ifndef PERIODIC_H_
#define PERIODIC_H_

#include <bits/stdc++.h>
using namespace std;

namespace Verification {
    class PeriodicState {
    public:
        virtual void setStateVal(int n, int k, int val) = 0;
        virtual bool readStateVal(int n, int k) = 0;
        virtual void reset() = 0;
    };

    class PeriodicStateVector: public PeriodicState {
    private:
        vector<vector<bool>> state;
    public:
        PeriodicStateVector(int n, int k) {
            state.resize(n);
            for (int i = 0; i < n; i++) {
                state[i].resize(k);
            }
        }
        void setStateVal(int n, int k, int val) {
            state[n][k] = val;
        }
        bool readStateVal(int n, int k) {
            return state[n][k];
        }
        void reset() {
            for (int i = 0; i < state.size(); i++) {
                fill(state[i].begin(), state[i].end(), 0);
            }
        }
    };

    class Periodic {
    private:
        int n, k;
        PeriodicState *state;
        vector<pair<int, int>> transition;
        vector<int> unsafe;

        vector<pair<int, int>> eventList;
    public:
        // number of states & periodic length
        // type 0: vector
        // type 1: unordered_set
        Periodic(int n, int k, int type = 1) {
            if (type == 1) {
                state = new PeriodicStateVector(n, k);
            }
            this->n = n;
            this->k = k;
            transition.resize(n);
            unsafe.resize(n);
            eventList.resize(k);
        }
        void addEdgeMachine(int start, int end0, int end1, int unsafe) {
            transition[start] = {end0, end1};
            this->unsafe[start] = unsafe;
        }
        void addEdgeEvent(int start, int end, int output) {
            eventList[start] = {end, output};
        }
        int solve(int start_state = 0) {
            clock_t start, end;
            start = clock();

            state->reset();
            int event_pointer = 0;
            int now_state = start_state;
            bool isUnsafe = false;
            while (true) {
                // printf("(%d, %d)\n", now_state, event_pointer);
                if (state->readStateVal(now_state, event_pointer)) {
                    break;
                }
                state->setStateVal(now_state, event_pointer, 1);

                if (unsafe[now_state]) {
                    isUnsafe = true;
                    break;
                }
                auto event = eventList[event_pointer];
                now_state = event.second == 0 ? transition[now_state].first: transition[now_state].second;
                event_pointer = event.first;
            }

            if (isUnsafe) cout << "[Result]\tUnsafe\n";
            else cout << "[Result]\tSafe\n";

            end = clock();
            double time_taken = double(end - start) / double(CLOCKS_PER_SEC); 
            cerr << "[Info]\tTime taken by solver: " << fixed  
                 << time_taken << setprecision(5); 
            cerr << " sec " << endl << endl; 
            return isUnsafe;
        }

        int solveAll(int start_state = 0) {
            clock_t start, end;
            start = clock();

            state->reset();
            bool isUnsafe = false;

            for (int event_start = 0; event_start < k; event_start++) {
                int event_pointer = event_start;
                int now_state = start_state;
                while (true) {
                    if (state->readStateVal(now_state, event_pointer)) {
                        break;
                    }
                    state->setStateVal(now_state, event_pointer, 1);

                    if (unsafe[now_state]) {
                        isUnsafe = true;
                        break;
                    }
                    auto event = eventList[event_pointer];
                    now_state = event.second == 0 ? transition[now_state].first: transition[now_state].second;
                    event_pointer = event.first;
                }    
            }

            if (isUnsafe) cout << "[Result]\tUnsafe\n";
            else cout << "[Result]\tSafe\n";

            end = clock();
            double time_taken = double(end - start) / double(CLOCKS_PER_SEC); 
            cerr << "[Info]\tTime taken by solver: " << fixed  
                 << time_taken << setprecision(5); 
            cerr << " sec " << endl << endl; 
            return isUnsafe;
        }
        ~Periodic() {
            delete state;
        }
    };
}

#endif // PERIODIC_H_