import hc_optimizer
import numpy as np
import operator as op


def random_partition(worker_num, cell_num):
    rand_cells = np.random.permutation(cell_num)
    groups = np.array_split(rand_cells, worker_num)
    ret = [i.tolist() for i in groups]
    return ret


# queries
twohop = {
    'name': 'twohop',
    'hc_sizes': [8, 8],
    'child_num_cols': [2, 2, 2],
    'child_sizes': [1114289, 1114289, 1114289],
    'join_conditions': [
        [(0, 1), (1, 0)],
        [(1, 1), (2, 0)]
    ]
}

# twitter
q1 = {
    'name': 'q1',
    'hc_sizes': [16, 16, 16],
    'child_num_cols': [2, 2, 2],
    'child_sizes': [1114289, 1114289, 1114289],
    'join_conditions': [
        [(0, 1), (1, 0)],
        [(1, 1), (2, 0)],
        [(2, 1), (0, 0)]
    ]
}

# 4-clique
q2 = {
    'name': 'q2',
    # 'hc_sizes': [4, 1, 8, 2],
    'hc_sizes': [8, 2, 32, 8],
    'child_num_cols': [2, 2, 2, 2, 2, 2],
    'child_sizes': [1114289, 1114289, 1114289, 1114289, 1114289, 1114289],
    'join_conditions': [
        [(0, 1), (1, 0)],
        [(1, 1), (2, 0), (5, 0), (4, 1)],
        [(2, 1), (3, 0), (5, 1)],
        [(3, 1), (0, 0), (4, 0)]
    ]
}

# freebase query 1
q3 = {
    'name': 'q3',
    # 'hc_sizes': [1, 4, 1, 4, 1, 4],
    'hc_sizes': [2, 8, 2, 8, 2, 8],
    'child_num_cols': [1, 2, 2, 1, 2, 2, 2, 2],
    'join_conditions': [
        [(0, 0), (1, 0)],
        [(1, 1), (2, 0)],
        [(2, 1), (5, 1), (6, 1)],
        [(3, 0), (4, 0)],
        [(4, 1), (5, 0)],
        [(6, 0), (7, 1)]
    ],
    'child_sizes': [
        26, 1100844, 1094294, 2, 1100844, 1094294, 1094294, 1100844
    ]
}

# freebase query 5
q4 = {
    'name': 'q4',
    # 'hc_sizes': [2, 2, 1, 2, 1, 2, 2, 2],
    'hc_sizes': [4, 4, 1, 4, 1, 4, 4, 4],
    'child_sizes': [
        1100844, 1094294, 1100844, 1094294,
        1094294, 1100844, 1100844, 1094294],
    'child_num_cols': [2, 2, 2, 2, 2, 2, 2, 2],
    'join_conditions': [
        [(0, 0), (2, 0)],
        [(0, 1), (1, 0)],
        [(1, 1), (5, 1)],
        [(2, 1), (3, 0)],
        [(3, 1), (7, 1)],
        [(4, 0), (6, 0)],
        [(4, 1), (5, 0)],
        [(6, 1), (7, 0)]
    ],
}


def random_hcs_allocation(server_num, cell_num, query, hc_sizes, repeat=10):
    costs = []
    max_wls = []
    for i in range(repeat):
        cost, max_wl = hc_optimizer.vcell_hcs_cost(
            random_partition(server_num, cell_num), hc_sizes,
            query['child_sizes'], query['child_num_cols'],
            query['join_conditions'])
        max_wls.append(max_wl)
        costs.append(cost)
        return min(max_wls), min(costs)


def hcs_allocation_compare(server_num, cell_num, queries):
    """
        Compute the workload by LP solution (fractional) and round down
    """
    for query in queries:
        # compute optimal solution and round_down
        wl, ds, r_wl, r_ds = hc_optimizer.frac_dim_sizes(
            server_num, query['child_sizes'],
            query['child_num_cols'], query['join_conditions'])
        # compute random allocation
        _, _, _, cell_ds = hc_optimizer.frac_dim_sizes(
            cell_num, query['child_sizes'],
            query['child_num_cols'], query['join_conditions'])
        real_cell_num = reduce(op.mul, cell_ds, 1)
        random_wl, _ = random_hcs_allocation(
            server_num, real_cell_num, query, cell_ds)
        print wl, r_wl, reduce(op.mul, r_ds, 1), random_wl, real_cell_num


if __name__ == '__main__':
    hcs_allocation_compare(65, 4096, [q1, q2, q3, q4])
