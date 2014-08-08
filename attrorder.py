# collect selectivity data from input, change attribute orders
# everything is hardcoded, but before deadline, who cares?

import json
import csv


def extract_info(tables):
    """
    Extract information from tables.
    Arguments:
        tables - input tables, in csv format
    Return:
    """
    return []


def cost(order, join_map, rel_info):
    """
    Estimate the cost of a query.
    Arguments:
        order - reorder the join_map according to this permutation
        join_map - an array of groups of equivalent classes of equi-join fields
        rel_info - an array containing information of all input relations
                        - card: cardinality
                        - cnt: array of number of unique value of columns
    Return:
        cost - a float number indicating the cost of current join order
    """
    return 0.0


def optimal_order(join_map, tables):
    """
    """
    return []


def change_order(order):
    """
    Change attribute order of a LFJ json query
    Arguments:
        - order: a new order (permutation)
    """
    with open("q1_local_lfj.json") as f:
        json_query = json.load(f)
    ops = json_query["plan"]["fragments"][0]["operators"]
    assert ops[16]["opType"] == "LeapFrogJoin"
    # get join map
    join_map = ops[16]["joinFieldMapping"]
    assert len(order) == len(join_map)
    # get children
    child_ids = ops[16]["argChildren"]
    children = []
    for child_id in child_ids:
        child_op = [op for op in ops if op["opId"] == child_id]
        assert len(child_op) == 1
        children.extend(child_op)
    # change sort order accordingly
    for child in children:
        print child


if __name__ == '__main__':
    change_order([0, 1, 2, 3, 4, 5])
