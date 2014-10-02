import hc_optimizer
import numpy as np


def random_partition(worker_num, cell_num):
    rand_cells = np.random.permutation(cell_num)
    groups = np.array_split(rand_cells, worker_num)
    ret = [i.tolist() for i in groups]
    print ret
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

twitter = {
    'name': 'twitter',
    'hc_sizes': [16, 16, 16],
    'child_num_cols': [2, 2, 2],
    'child_sizes': [1114289, 1114289, 1114289],
    'join_conditions': [
        [(0, 1), (1, 0)],
        [(1, 1), (2, 0)],
        [(2, 1), (0, 0)]
    ]
}

clique = {
    'name': 'clique',
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

fb_q1 = {
    'name': 'fb_q1',
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

fb_q5 = {
    'name': 'fb_q5',
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


def random_hcs_allocation(server_num, cell_num, queries, repeat=10):
    for query in queries:
        costs = []
        max_wls = []
        for i in range(repeat):
            cost, max_wl = hc_optimizer.vcell_hcs_cost(
                random_partition(server_num, cell_num), query['hc_sizes'],
                query['child_sizes'], query['child_num_cols'],
                query['join_conditions'])
            max_wls.append(max_wl)
            costs.append(cost)
        print query['name']
        print min(max_wls)
        print min(costs)


if __name__ == '__main__':
    # random_hcs_allocation(64, 4096, [clique, twitter, fb_q1, fb_q5])
    random_hcs_allocation(4, 64, [twohop])
