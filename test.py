from hc_optimizer import (workload,
                          reversed_index,
                          vcell_hcs_cost,
                          get_dim_sizes_bfs,
                          frac_dim_sizes,
                          coordinate_to_vs)
import unittest


class TestOpimizerFunctions(unittest.TestCase):
    ''' unit test of optimizer
    '''
    def test_workload_1(self):
        """A(x,y,z) :- R(x,y),S(y,z),T(z,x)"""
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        dim_sizes = [3, 3, 3]
        child_sizes = [27, 9, 9]
        self.assertEqual(
            workload(dim_sizes, child_sizes, r_index), 5)

    def test_workload_2(self):
        """A(x,y,z) :- R(x,y),S(y,z), T(z,p)"""
        join_conditions = [[[0, 1], [1, 0]], [[1, 1], [2, 0]]]
        dim_sizes = [4, 6]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        child_sizes = [24, 36, 48]
        self.assertEqual(
            workload(dim_sizes, child_sizes, r_index),
            24.0 / 4.0 + 36.0 / 24.0 + 48.0 / 6.0)

    def test_optimizer(self):
        # 1. symmetric case: A(x,y,z) :- R(x,y), S(y,z), T(z,x)
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        dim_sizes = [4, 4, 4]
        child_num_cols = [2, 2, 2]
        r_index = reversed_index(child_num_cols, join_conditions)
        child_sizes = [50, 50, 50]
        wl_by_opt, _ = get_dim_sizes_bfs(
            64, child_sizes, child_num_cols,  join_conditions)
        self.assertEqual(wl_by_opt, workload(dim_sizes, child_sizes, r_index))

    def test_frac_dim_size(self):
        join_conditions = [
            [[0, 1], [1, 0]], [[1, 1], [2, 0]], [[0, 0], [2, 1]]]
        child_num_cols = [2, 2, 2]
        child_sizes = [20, 20, 20]
        wl, dim_sizes = frac_dim_sizes(
            64, child_sizes, child_num_cols, join_conditions)
        self.assertAlmostEqual(wl, 60.0/16.0, delta=0.001)

    def test_frac_dim_size_2(self):
        join_conditions = [[[0, 1], [1, 0]], [[1, 1], [2, 0]],
                          [[2, 1], [3, 0]]]
        child_num_cols = [2, 2, 2, 2]
        child_sizes = [36, 72, 64, 36]
        frac_dim_sizes(64, child_sizes, child_num_cols, join_conditions)

    def free_base_q1(self):
        join_conditions = [
            [[0, 0], [1, 0]],
            [[1, 1], [2, 0]],
            [[2, 1], [5, 1], [6, 1]],
            [[3, 0], [4, 0]],
            [[4, 1], [5, 0]],
            [[6, 0], [7, 0]],
            [[7, 1], [8, 0]]
            ]
        child_sizes = [
            1, 1000000, 1000000,
            1, 1000000, 1000000,
            1000000, 1000000, 59000000]
        child_num_cols = [1, 2, 2, 1, 2, 2, 2, 2, 2]
        wl_frac, dim_sizes_f = frac_dim_sizes(
            64, child_sizes, child_num_cols, join_conditions)
        wl_by_opt, dim_sizes = get_dim_sizes_bfs(
            64, child_sizes, child_num_cols,  join_conditions)
        print wl_frac, dim_sizes_f
        print wl_by_opt, dim_sizes

    def test_fb_q1_2(self):
        join_conditions = [
            [[0, 0], [1, 0]],
            [[1, 1], [2, 0]],
            [[2, 1], [3, 1], [4, 1]],
            [[3, 0], [6, 1]],
            [[4, 0], [5, 0]],
            [[5, 1], [7, 0]],
            [[6, 0], [8, 0]]]
        child_sizes = [
            1, 1000000, 1000000, 1000000, 1000000,
            1000000, 1000000, 59000000, 1]
        child_num_cols = [1, 2, 2, 2, 2, 2, 2, 2, 1]
        wl_by_opt, dim_sizes = get_dim_sizes_bfs(
            64, child_sizes, child_num_cols,  join_conditions)
        ndim_sizes = (1, 1, 2, 1, 1, 4, 8)
        r_index = reversed_index(child_num_cols, join_conditions)
        print workload(ndim_sizes, child_sizes, r_index)
        print wl_by_opt, dim_sizes

    def test_coordinate_to_vs(self):
        assert coordinate_to_vs((1, 2, 4), (2, 4, 5)) == 34

    def test_vs_assignment(self):
        # Result(x, y, z, p) :- R(x, y), S(y, z), T(z, p)
        join_conditions = [[(0, 1), (1, 0)], [(1, 1), (2, 0)]]
        child_sizes = [100, 50, 100]
        assignment_1 = [(0, 1), (2, 3), (4, 5), (6, 7)]
        assignment_2 = [(2, 5), (1, 4), (0, 3), (6, 7)]
        child_num_cols = [2, 2, 2]
        hc_sizes = [2, 4]
        r1, max_wl = vcell_hcs_cost(
            assignment_1, hc_sizes, child_sizes,
            child_num_cols, join_conditions)
        assert r1 == 450
        r2, max_wl = vcell_hcs_cost(
            assignment_2, hc_sizes, child_sizes,
            child_num_cols, join_conditions)
        assert r2 == 550
