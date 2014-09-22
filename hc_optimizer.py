import json
import collections
from pulp import *
from operator import mul, itemgetter
import math
import itertools


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':'))


def reversed_index(child_num_cols, join_conditions):
    """ Return reverse index of join_conditions.
        r_index[i][j] -> k, j-th column of i-th child is in k-th
        join conditions, if the column is not joined, its r_index value will
        be -1
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


def coordinate_to_vs(coordinate, hc_sizes):
    """
        Return the virtual server id of a given coordinate.
        Argument:
            coordinate - the input coordiante that has the len(hc_sizes) dims
            hc_sizes - sizes of dimensions of HyperCube
    """
    assert len(coordinate) == len(hc_sizes)
    vs = 0
    for i, s in enumerate(coordinate):
        vs += s * reduce(mul, hc_sizes[i+1:], 1)
    return vs


def shuffle_cost_vs_assignment(assignment, hc_sizes, child_sizes,
                               child_num_cols, join_conditions):
    """
        Calculate shuffle cost of a virtual server assignment.
        Argument:
            assignment - a partition of virtual server
            child_sizes - sizes of input relations
            child_num_cols - num of cols of input relations
            join_conditions - join condition map, equal classes of joined cols
    """
    assert sum(len(part) for part in assignment) == reduce(mul, hc_sizes, 1)
    # 1. compute reversed index and vs_rs_map
    r_index = reversed_index(child_num_cols, join_conditions)
    vs_rs_map = dict()
    for i, partition in enumerate(assignment):
        for vs in partition:
            vs_rs_map[vs] = i
    # 2. compute shuffle cost of each relation
    cost = 0.0
    for i, cols in enumerate(r_index):
        # get subcube dims and their sizes
        subc_dims = sorted([order for order in cols if order != -1])
        subc_sizes = [hc_sizes[d] for d in subc_dims]
        # get unjoined dims and their sizes
        un_joined_dims = [
            d for d in range(len(hc_sizes)) if d not in subc_dims]
        un_joined_sizes = [hc_sizes[d] for d in un_joined_dims]
        num_voxels = reduce(mul, subc_sizes, 1)         # number of voxels
        voxel_wl = child_sizes[i]/float(num_voxels)     # workload per voxel
        shuffle_ranges = [range(s) for s in subc_sizes]
        broadcast_ranges = [range(s) for s in un_joined_sizes]
        for vox_coor in itertools.product(*shuffle_ranges):
            rs = set()
            for brcst_coor in itertools.product(*broadcast_ranges):
                idx_coor = zip(subc_dims, vox_coor) + zip(
                    un_joined_dims, brcst_coor)
                coor = map(itemgetter(1), sorted(idx_coor))
                vs = coordinate_to_vs(coor, hc_sizes)
                rs.add(vs_rs_map[vs])
            cost += len(rs) * voxel_wl
    return cost
