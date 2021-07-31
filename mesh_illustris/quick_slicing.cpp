// Copyright (c) 2021 Bill Chen
// License: MIT (see LICENSE)

#include <iostream>
#include <vector>
#include <cmath>
  
using namespace std;

vector<long long> slicing(
    long long * lower, 
    long long * upper, 
    long long * mark, 
    long long * index, 
    long long depth){
    /*Slice the index file according to lower/upper boundaries.*/

    long long idx_1d_lower;
    long long idx_1d_upper;

    long long start;
    long long end;

    vector<long long> target;

    for (long long i = lower[0]; i < upper[0]; ++i){
        for (long long j = lower[1]; j < upper[1]; ++j){
            idx_1d_lower = (i<<(depth*2)) + (j<<depth) + lower[2];
            idx_1d_upper = (i<<(depth*2)) + (j<<depth) + upper[2];

            start = mark[idx_1d_lower];
            end = mark[idx_1d_upper];

            target.insert(target.begin(), index+start, index+end);
        }
    }

    return target;
}