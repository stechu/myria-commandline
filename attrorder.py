

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
