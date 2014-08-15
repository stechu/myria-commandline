import json
import argparse
import collections
from pulp import *
from operator import mul
import math

#parse args
parser = argparse.ArgumentParser(
    description='collect running time of workers of a query')
parser.add_argument("-query", type=str, help="query json file")
parser.add_argument("-worker_number", type=int, help="number of workers")
parser.add_argument("-e", type=float, help="relax parameter")
args = parser.parse_args()


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':'))


def reversed_index(child_num_cols, join_conditions):
    """ Return reverse index of join_conditions.
        r_index[i][j] -> k, j-th column of i-th child is in k-th
        join conditions
    """
    # make it -1 first
    r_index = [[-1] * num_cols for num_cols in child_num_cols]
    for i, jf_list in enumerate(join_conditions):
        for jf in jf_list:
            r_index[jf[0]][jf[1]] = i
    return r_index


# compute work load give a hyper cube size assignment
def workload(dim_sizes, child_sizes, r_index):
    load = float(0)
    for i, size in enumerate(child_sizes):
        scale = 1
        for index in r_index[i]:
            if index != -1:
                scale = scale * dim_sizes[index]
        load = load + float(child_sizes[i])/float(scale)
    return load


# using recursive call: will expode the stack
def enum_dim_sizes(visited, dim_sizes, num_server,
                   child_sizes, r_index):
    visited.add(dim_sizes)
    yield (workload(dim_sizes, child_sizes, r_index), dim_sizes)
    for i, d in enumerate(dim_sizes):
        new_dim_sizes = dim_sizes[0:i] + tuple([dim_sizes[i]+1])
        new_dim_sizes += dim_sizes[i+1:]
        if product_not_greater(new_dim_sizes, num_server)\
           and new_dim_sizes not in visited:
            for x in enum_dim_sizes(visited, new_dim_sizes, num_server,
                                    child_sizes, r_index):
                yield x


def get_dim_size_dfs(num_server, child_sizes, child_num_cols, join_conditions):
    firstDims = tuple([1 for x in join_conditions])
    r_index = reversed_index(child_num_cols, join_conditions)
    return min(enum_dim_sizes(set(), firstDims, num_server,
                              child_sizes, r_index))


# using bfs to get optimal dimension sizes
def get_dim_sizes_bfs(num_server, child_sizes,
                      child_num_cols, join_conditions):
    r_index = reversed_index(child_num_cols, join_conditions)
    visited = set()
    toVisit = collections.deque()
    toVisit.append(tuple([1 for i in join_conditions]))
    min_work_load = sum(child_sizes)
    while len(toVisit) > 0:
        dim_sizes = toVisit.pop()
        if workload(dim_sizes, child_sizes, r_index) < min_work_load:
            min_work_load = workload(dim_sizes, child_sizes, r_index)
            opt_dim_sizes = dim_sizes
        visited.add(dim_sizes)
        for i, d in enumerate(dim_sizes):
            new_dim_sizes = dim_sizes[0:i] +\
                tuple([dim_sizes[i]+1]) + dim_sizes[i+1:]
            if reduce(mul, new_dim_sizes, 1) <= num_server\
               and new_dim_sizes not in visited:
                toVisit.append(new_dim_sizes)
    return (min_work_load, opt_dim_sizes)


# get optimal fracitonal dim size, see P9 in http://arxiv.org/abs/1401.1872
def frac_dim_sizes(num_server, child_sizes, child_num_cols, join_conditions):
    # get relation -> variable mapping
    rel_var_amp = dict()
    for idx, flist in enumerate(join_conditions):
        for (r, v) in flist:
            if r in rel_var_amp:
                rel_var_amp[r].append(idx)
            else:
                rel_var_amp[r] = [idx]
    # LP problem formulation
    prob = LpProblem("Hyper Cube Size", LpMinimize)
    # transform relations sizes to log scale
    log_rel_size = [math.log(s, num_server) for s in child_sizes]
    # define share size exponents
    share_ex_vars = LpVariable.dicts("e", range(0, len(join_conditions)), 0, 1)
    # objective function
    obj = LpVariable("obj", 0, None)
    prob += lpSum(obj)
    # constraint: sum of share exponents is at most 1
    prob += lpSum(share_ex_vars) <= 1
    # constraints: work load on each relation is smaller than obj
    for idx, val in enumerate(log_rel_size):
        prob += lpSum([share_ex_vars[var] for var
                       in rel_var_amp[idx]]) + obj >= log_rel_size[idx]
    prob.solve()
    answer = dict()
    for v in prob.variables():
        answer[v.name] = v.value()
    logs = [answer["e_{}".format(i)] for i in range(0, len(join_conditions))]
    # the solution is in log scale, recover it
    dim_sizes = [math.pow(num_server, x) for x in logs]
    r_index = reversed_index(child_num_cols, join_conditions)
    return (workload(dim_sizes, child_sizes, r_index), dim_sizes)
