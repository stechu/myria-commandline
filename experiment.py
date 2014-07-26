import client
import csv
import queries
import itertools
import numpy as np

hostname = "dbserver02.cs.washington.edu"
port = "10032"

client.init_connection(hostname, port)


def experiment(filename, exp_queries):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["name", "qid", "time", "algebra", "profilingMode", "success"])
        for query in exp_queries:
            # submit queries
            result, status = client.execute_query(query)
            _, algebra, profie, _, name = query
            # log experiment result
            if result == 'success':
                time = float(status["elapsedNanos"]) / client.NANO_IN_ONE_SEC
                writer.writerow(
                    [name, status["queryId"], time, algebra, profie, result])
            else:
                writer.writerow(
                    [name, "N.A.", "N.A.", algebra, profie, result])


exp_raw_queries = [
    (queries.triangle, 'triangle'),
    (queries.fb_q1, 'fb_q1'),
    (queries.rectangle, 'rectangle'),
    (queries.fb_q2, 'fb_q2'),
    (queries.two_rings, 'two_rings'),
    (queries.fb_q3, 'fb_q3'),
    (queries.clique, 'clique'),
    (queries.fb_q4, 'fb_q4')
]

phys_algebras = [
    ('RS_HJ',),
    ('HC_HJ',),
    ('BR_HJ',),
    ('HC_LFJ',),
    ('BR_LFJ',)
]

languages = [('myrial',)]


# experiment 1:  resouce usage
def resource_exp():
    profilingModes = [('RESOURCE',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment("resource_exp.csv", exp_queries)


# experiment 2: profile query execution only
def profile_exp():
    profilingModes = [('QUERY',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment("profile_exp.csv", exp_queries)


# experiment 3: cold cache experiment
def cold_cache_exp(filename):
    profilingModes = [('NONE',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


def collect_network_data(queryId):
    """collect skew and """
    send = list(client.connection.get_sent_logs(queryId))
    # sanitiy checking
    assert len(send[0]) == 4
    # remove header
    send = send[1:]
    # convert to long
    send = [map(long, r) for r in send]
    # compute total number
    total_num_tuples = sum([r[3] for r in send])
    # group by fragmentid
    key_func = lambda x: x[1]
    send = sorted(send, key=lambda x: x[1])
    sends = itertools.groupby(send, key_func)
    groups = []
    for fid, shuffles in sends:
        groups.append([r for r in shuffles])

    # compute skew per group
    def compute_skew(group):
        data = [r[3] for r in group]
        skew = np.max(data)/np.mean(data)
        return skew
    skews = map(compute_skew, groups)
    # return number of tuples being shuffled, and max skew
    return total_num_tuples, max(skews)


if __name__ == '__main__':
    #resource_exp()
    #profile_exp()
    cold_cache_exp("cold_cache_1.csv")
    cold_cache_exp("cold_cache_2.csv")
    cold_cache_exp("cold_cache_3.csv")
    cold_cache_exp("cold_cache_4.csv")
    cold_cache_exp("cold_cache_5.csv")
    #q = ('myrial', "RS_HJ", "NONE", queries.triangle, 'whatever')
    #execute_query(q)
    # collect_network_data(1031)
