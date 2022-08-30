def get_implied_cases(K):
    K = K+1
    sub2whole = {}
    whole2sub = {}
    for i in range(1,K):
        for j in range(i,K):
            for k in range(1,i+1):
                for l in range(j, K):
                    if (i,j) not in whole2sub:
                        whole2sub[(i,j)] = {(i,j):0}
                    if (k,l) not in sub2whole:
                        sub2whole[(k,l)] = {(k,l):0}
                    if (i,j) not in sub2whole[(k,l)]:
                        sub2whole[(k,l)][(i,j)] = 0
                    if (k,l) not in whole2sub[(i,j)]:
                        whole2sub[(i,j)][(k,l)] = 0
    for i in range(1,K):
        for j in range(i,K):
            for k in range(i,K):
                for l in range(k, min(k//i*j + k%i+1, K)):
                    if (i,j) not in sub2whole:
                        sub2whole[(i,j)] = {(i,j):0}
                    if (k,l) not in whole2sub:
                        whole2sub[(k,l)] = {(k,l):0}
                    if (i,j) not in whole2sub[(k,l)]:
                        whole2sub[(k,l)][(i,j)] = 0
                    if (k,l) not in sub2whole[(i,j)]:
                        sub2whole[(i,j)][(k,l)] = 0
    return sub2whole, whole2sub