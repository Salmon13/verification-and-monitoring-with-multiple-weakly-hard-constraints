#ifndef WEAKLYHARD_H_
#define WEAKLYHARD_H_

#include <bits/stdc++.h>
using namespace std;

namespace Verification {
    class WeaklyHardState {
    public:
        virtual void setStateVal(int n, int mask1, int mask2, int val) = 0;
        virtual bool readStateVal(int n, int mask1, int mask2) = 0;
        virtual void reset() = 0;
    };

    class WeaklyHardStateVector: public WeaklyHardState {
    private:
        vector<vector<vector<bool>>> state;
    public:
        WeaklyHardStateVector(int n, int k) {
            state.resize(n);
            for (int i = 0; i < n; i++) {
                state[i].resize(1 << k);
                for(int j = 0; j < 1 << k; j++) {
                    state[i][j].resize(1 << k);
                }
            }
        }
        void setStateVal(int n, int mask1, int mask2, int val) {
            state[n][mask1][mask2] = val;
        }
        bool readStateVal(int n, int mask1, int mask2) {
            return state[n][mask1][mask2];
        }
        void reset() {
            for (int i = 0; i < state.size(); i++) {
            }
        }
    };

    class WeaklyHardSingle {
    private:
        int n, m, k;
        WeaklyHardState *state;
        vector<pair<pair<int, int>, pair<int, int>>> transition;
        vector<int> unsafe;
        vector<int> bitcount;
    public:
        // number of states & periodic length
        // type 0: vector
        // type 1: unordered_set
        WeaklyHardSingle(int n, int m, int k, int type = 1) {
            if (type == 1) {
                state = new WeaklyHardStateVector(n, k);
            }
            this->n = n;
            this->m = m;
            this->k = k;
            transition.resize(n);
            unsafe.resize(n);
            bitcount.resize(1 << k);
            for (int i = 0; i < (1 << k); i++) {
                int val = i;
                int cnt = 0;
                while (val) {
                    if (val&1) cnt++;
                    val >>= 1;
                }
                bitcount[i] = cnt;
            }
        }
        void addEdgeMachine(int start, int end0, int end1, int end2, int end3, int unsafe) {
            transition[start] = {{end0, end1}, {end2, end3}};
            this->unsafe[start] = unsafe;
        }
        int solve(int start_state = 0) {
            clock_t start, end;
            start = clock();
            int now_state = start_state;
            int now_mask1 = 0, now_mask2 = 0;
            bool isUnsafe = false;

            queue<pair<int, pair<int, int>>> que;
            que.push({now_state, {now_mask1, now_mask2}});
            state->setStateVal(now_state, now_mask1, now_mask2, 1);
            while (que.size()) {
                auto out = que.front();
                que.pop();
                now_state = out.first;
                now_mask1 = out.second.first;
                now_mask2 = out.second.second;
                //printf("mask : %d %d\n", now_mask1, now_mask2);
                if (unsafe[now_state]) {
                    isUnsafe = true;
                    //printf("cnt : %d, state : %d\n", cnt, now_state);
                    break;
                }
                // get good event
                if (true) {
                    int nxt_state = transition[now_state].first.first;
                    int nxt_mask1 = (now_mask1 * 2) % (1 << k);
                    int nxt_mask2 = (now_mask2 * 2) % (1 << k);
                    if (!state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                        state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                        que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                    }
                }
                // get bad event
                if (true) {
                    int nxt_state = transition[now_state].first.second;
                    int nxt_mask1 = (now_mask1 * 2 + 1) % (1 << k);
                    int nxt_mask2 = (now_mask2 * 2) % (1 << k);
                    if (bitcount[nxt_mask1] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                        state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                        que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                    }
                }
                if (true) {
                    int nxt_state = transition[now_state].second.first;
                    int nxt_mask1 = (now_mask1 * 2) % (1 << k);
                    int nxt_mask2 = (now_mask2 * 2 + 1) % (1 << k);
                    if (bitcount[nxt_mask2] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                        state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                        que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                    }
                }
                if (true) {
                    int nxt_state = transition[now_state].second.second;
                    int nxt_mask1 = (now_mask1 * 2 + 1) % (1 << k);
                    int nxt_mask2 = (now_mask2 * 2 + 1) % (1 << k);
                    if (bitcount[nxt_mask1] <= m && bitcount[nxt_mask2] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                        state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                        que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                    }
                }
            }

            // if (isUnsafe) cout << "[Result] Unsafe\n";
            // else cout << "[Result] Safe\n";

            end = clock();
            // double time_taken = double(end - start) / double(CLOCKS_PER_SEC); 
            // cout << "[Info] Time taken by solver: " << fixed  
            //      << time_taken << setprecision(5); 
            // cout << " sec " << endl << endl; 
            return isUnsafe;
        }
        ~WeaklyHardSingle() {
            delete state;
        }
    };
    class WeaklyHardReuse {
    private:
        int n, k;
        WeaklyHardState *state;
        vector<pair<pair<int, int>, pair<int, int>>> transition;
        vector<int> unsafe;
        vector<int> bitcount;
    public:
        // number of states & periodic length
        // type 0: vector
        // type 1: unordered_set
        WeaklyHardReuse(int n, int k, int type = 1) {
            if (type == 1) {
                state = new WeaklyHardStateVector(n, k);
            }
            this->n = n;
            this->k = k;
            transition.resize(n);
            unsafe.resize(n);
            bitcount.resize(1 << k);
            for (int i = 0; i < (1 << k); i++) {
                int val = i;
                int cnt = 0;
                while (val) {
                    if (val&1) cnt++;
                    val >>= 1;
                }
                bitcount[i] = cnt;
            }
        }
        void addEdgeMachine(int start, int end0, int end1, int end2, int end3, int unsafe) {
            transition[start] = {{end0, end1}, {end2, end3}};
            this->unsafe[start] = unsafe;
        }
        int solve(int start_m = 1, int start_state = 0) {
            clock_t start, end;
            // start = clock();
            int now_state = start_state;
            int now_mask1 = 0, now_mask2 = 0;
            bool isUnsafe = false;

            queue<pair<int, pair<int, int>>> que;
            vector<pair<int, pair<int, int>>> nextQue;

            int m;
            for (m = start_m; m <= k; m++) {
                int nowid = m % 2;
                int nxtid = (m + 1) % 2;
                if (m == start_m) {
                    que.push({now_state, {now_mask1, now_mask2}});
                    state->setStateVal(now_state, now_mask1, now_mask2, 1);
                } else {
                    for (auto pr: nextQue) {
                        que.push(pr);
                        state->setStateVal(pr.first, pr.second.first, pr.second.second, 1);
                    }
                    nextQue.clear();
                }
                
                while (que.size()) {
                    auto out = que.front();
                    que.pop();
                    now_state = out.first;
                    now_mask1 = out.second.first;
                    now_mask2 = out.second.second;
                    if (unsafe[now_state]) {
                        isUnsafe = true;
                        break;
                    }
                    // get good event
                    if (true) {
                        int nxt_state = transition[now_state].first.first;
                        int nxt_mask1 = (now_mask1 * 2) % (1 << k);
                        int nxt_mask2 = (now_mask2 * 2) % (1 << k);
                        if (!state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                            state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                            que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                        }
                    }
                    // get bad event
                    if (true) {
                        int nxt_state = transition[now_state].first.second;
                        int nxt_mask1 = (now_mask1 * 2 + 1) % (1 << k);
                        int nxt_mask2 = (now_mask2 * 2) % (1 << k);
                        if(bitcount[nxt_mask1] > m){
                            nextQue.push_back({nxt_state, {nxt_mask1, nxt_mask2}});
                        }else if (bitcount[nxt_mask1] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                            state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                            que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                        }
                    }
                    if (true) {
                        int nxt_state = transition[now_state].second.first;
                        int nxt_mask1 = (now_mask1 * 2) % (1 << k);
                        int nxt_mask2 = (now_mask2 * 2 + 1) % (1 << k);
                        if(bitcount[nxt_mask2] > m){
                            nextQue.push_back({nxt_state, {nxt_mask1, nxt_mask2}});
                        }else if (bitcount[nxt_mask2] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                            state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                            que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                        }
                    }
                    if (true) {
                        int nxt_state = transition[now_state].second.second;
                        int nxt_mask1 = (now_mask1 * 2 + 1) % (1 << k);
                        int nxt_mask2 = (now_mask2 * 2 + 1) % (1 << k);
                        if(bitcount[nxt_mask1] > m || bitcount[nxt_mask2] > m){
                            nextQue.push_back({nxt_state, {nxt_mask1, nxt_mask2}});
                        }else if (bitcount[nxt_mask1] <= m && bitcount[nxt_mask2] <= m && !state->readStateVal(nxt_state, nxt_mask1, nxt_mask2)) {
                            state->setStateVal(nxt_state, nxt_mask1, nxt_mask2, 1);
                            que.push({nxt_state, {nxt_mask1, nxt_mask2}});
                        }
                    }
                }

                // printf("(%d, %d): ",m, k);
                if (isUnsafe) {
                    // return m;
                    break;
                }
            }
            

            // end = clock();
            //double time_taken = double(end - start) / double(CLOCKS_PER_SEC); 

            /*
            if (isUnsafe) cout << "[Result] Unsafe\n";
            else cout << "[Result] Safe\n";
            cout << "[Info] Time taken by solver: " << fixed  
                 << time_taken << setprecision(5); 
            cout << " sec " << endl << endl; 
            */
            // return k + 1;
            return m;
        }
        ~WeaklyHardReuse() {
            delete state;
        }
    };
}

#endif // WEAKLYHARD_H_
