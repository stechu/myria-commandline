# collect selectivity data from input, change attribute orders
# everything is hardcoded, but before deadline, who cares?

from operator import itemgetter
import itertools
import csv


def extract_info(table_files):
    """
    Extract information from tables.
    Arguments:
        tables - input tables, in csv format
    Return:
    """
    ret = []
    for fname in table_files:
        table = {}
        # read data from csv
        with open(fname, "rb") as f:
            reader = csv.reader(f)
            data = [r for r in reader]
        # record header and arity
        table["header"] = data[0]
        assert data[0] > 0
        table["arity"] = len(data[0])
        # record unique values for each col
        values = [set() for col in data[0]]
        for row in data[1:]:
            for i, value in enumerate(row):
                values[i].add(value)
        v_cnt = [len(value_set) for value_set in values]
        table["value_cnt"] = v_cnt
        table["rows"] = len(data) - 1
        ret.append(table)
    return ret


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


def change_order(json_query, order):
    """
    Change attribute order of a LFJ json query
    Arguments:
        - order: a new order (permutation)
    """
    lfj_pos = 16    # NOTE: this is hardcoded!
    jfm = "joinFieldMapping"
    ops = json_query["plan"]["fragments"][0]["operators"]
    assert ops[lfj_pos]["opType"] == "LeapFrogJoin"
    # 1. get join map
    join_map = ops[lfj_pos][jfm]
    assert len(order) == len(join_map)
    # 2. get children
    child_ids = ops[lfj_pos]["argChildren"]
    children = []
    for child_id in child_ids:
        # store child and its idx
        child_idx = [
            i for i, op in enumerate(ops) if op["opId"] == child_id]
        assert len(child_idx) == 1
        children.extend(child_idx)
    # 3. re-order join map
    new_join_map = []
    for o in order:
        new_join_map.append(join_map[o])
    # 4. change sort order accordingly
    attr_list = []  # (dim_idx, table_index, col_idx)
    for i, equi_class in enumerate(new_join_map):
        for table_idx, col_idx in equi_class:
            attr_list.append((i, table_idx, col_idx))
    attr_list = sorted(attr_list, key=itemgetter(1))
    attr_list = itertools.groupby(attr_list, key=itemgetter(1))
    attr_with_order = []
    for table_idx, grp in attr_list:
        attr_with_order.append(sorted(list(grp)))
    new_sort_order = []
    for attrs in attr_with_order:
        new_sort_order.append([col for dim, table, col in attrs])
    assert len(new_sort_order) == len(children)
    # 5. put changed lfj and sort back
    ops[lfj_pos][jfm] = new_join_map
    for cols, child_idx in zip(new_sort_order, children):
        ops[child_idx]["argSortColumns"] = cols
    return json_query

if __name__ == "__main__":
    extract_info(["table1.csv", "table2.csv"])
