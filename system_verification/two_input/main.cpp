#include <bits/stdc++.h>

#include "periodic.h"
#include "weaklyhard.h"

using namespace std;


int main(int argc, char **argv) {

    if (strcmp(argv[1], "weaklyhardsingle") == 0) {
        if (argc != 6) {
            cerr << "[Error] Please run the program with command: ./main weaklyhardsingle input_file K out_cost_matrix_file out_boundary_file" << endl;
            return 0;
        }
        int n;
        ifstream fin(argv[2]);
        fin >> n;
        vector<pair<pair<pair<int, int>, pair<int, int>>, int>> transition;
        for (int i = 0; i < n; i++) {
            int s0, s1, s2, s3, unsafe;
            fin >> s0 >> s1 >> s2 >> s3 >> unsafe;
            transition.push_back({{{s0, s1}, {s2, s3}}, unsafe});
        }

        int K = atoi(argv[3]);

        vector<vector<int>> result(K + 1);

        clock_t start, end;
        start = clock();
        double cost_matrix[K + 1][K + 1] = {0};

        for (int k = 1; k <= K; k++) {
            for (int m = 0; m <= k; m++) {
                clock_t single_start = clock();
                Verification::WeaklyHardSingle solver(n, m, k);
                for (int i = 0; i < n; i++) {
                    solver.addEdgeMachine(i, transition[i].first.first.first, transition[i].first.first.second, transition[i].first.second.first, transition[i].first.second.second, transition[i].second);
                }
                result[k].push_back(solver.solve());
                //printf("(%d, %d)\n", m, k);
                // cost_matrix[m][k] = clock() - single_start;
                cost_matrix[m][k] = double(clock() - single_start) / double(CLOCKS_PER_SEC);
            }
        }

        end = clock();
        double time_taken = double(end - start) / double(CLOCKS_PER_SEC);

        // cout << time_taken << setprecision(5) << endl;

        cout << "[Info] Total time taken by L-BFS: " << fixed
             << time_taken << setprecision(5);
        cout << " sec " << endl;

        /*
        for (int i = 1; i <= K; i++) {
            printf("K = %d\t:", i);
            for (int x: result[i]) {
                printf(" %d", x);
            }
            puts("");
        }

        for (int i = 1; i <= K; i++) {
            printf("%d\n", result[i].size());
        }
        */

        // log stuff

        int boundary[K + 1] = {0};
        for (int i = 1; i <= K; i++) {
            int b = -1;
            for (int x: result[i]) {
                if(x == 1)
                    break;
                ++b;
            }
            boundary[i] = b;
        }

        FILE *fp;
        fp = fopen(argv[4], "w+");
        for(int m = 0; m <= K; ++m) {
            for(int k = 0; k <= K; ++k) {
                fprintf(fp, "%lf%s", cost_matrix[m][k], k == K ? "\n" : ",");
            }
        }
        fclose(fp);

        fp = fopen(argv[5], "w+");
        for (int i = 0; i <= K; ++i) {
            fprintf(fp, "%d%s", boundary[i], i == K ? "\n" : ",");
        }
        fclose(fp);

    }
    else if (strcmp(argv[1], "weaklyhardreuse") == 0) {
        if (argc != 4) {
            cerr << "[Error] Please run the program with command: ./main weaklyhardreuse input_file K" << endl;
            return 0;
        }
        int n;
        ifstream fin(argv[2]);
        fin >> n;
        vector<pair<pair<pair<int, int>, pair<int, int>>, int>> transition;
        for (int i = 0; i < n; i++) {
            int s0, s1, s2, s3, unsafe;
            fin >> s0 >> s1 >> s2 >> s3 >> unsafe;
            transition.push_back({{{s0, s1}, {s2, s3}}, unsafe});
        }

        int K = atoi(argv[3]);


        vector<vector<int>> result(K + 1);
        int prevm = 1;

        clock_t start, end;
        start = clock();

        for (int k = 1; k <= K; k++) {
            // printf("(%d)\n", k);
            Verification::WeaklyHardReuse solver(n, k);
            for (int i = 0; i < n; i++) {
                solver.addEdgeMachine(i, transition[i].first.first.first, transition[i].first.first.second, transition[i].first.second.first, transition[i].first.second.second, transition[i].second);
            }
            int ret = solver.solve(prevm);
            prevm = ret;
            for (int i = 0; i < ret; i++) {
                result[k].push_back(0);
            }
            if (ret != k + 1) {
                result[k].push_back(1);
            }
        }

        end = clock();
        double time_taken = double(end - start) / double(CLOCKS_PER_SEC);

        // cout << time_taken << setprecision(5) << endl;

        cout << "[Info] Total time taken by DL-BFS: " << fixed
             << time_taken << setprecision(5);
        cout << " sec " << endl;

        for (int i = K; i >= 1; i--) {
            printf("K = %d\t:", i);
            for (int x: result[i]) {
                printf(" %d", x);
            }
            puts("");
        }

        // for (int i = 1; i <= K; i++) {
        //     printf("%d\n", result[i].size());
        // }

    }
}
