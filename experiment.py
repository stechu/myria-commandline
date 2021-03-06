import client
import csv
import queries
import scalability_queries
import itertools
from operator import itemgetter

hostname = "dbserver02.cs.washington.edu"
port = "10032"
num_servers = 64

client.init_connection(hostname, port)


def experiment(filename, exp_queries, workers="ALL"):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["name", "qid", "time", "algebra",
             "profilingMode", "output", "success"])
        for query in exp_queries:
            # submit queries
            lang, algebra, profile, query_str, name = query
            if query_str.find("store") == -1:
                output_name = "{}_{}".format(name, algebra)
                query_str += "store(query, {});\n".format(output_name)
            else:
                output_name = "defined"
            #    raise ValueError("stored relation cannot be pre-defined.")
            actual_query = (lang, algebra, profile, query_str, name)
            if name == "worker_2":
                new_workers = list(range(1, 3))
            elif name == "worker_4":
                new_workers = list(range(1, 5))
            elif name == "worker_8":
                new_workers = list(range(1, 9))
            elif name == "worker_16":
                new_workers = list(range(1, 17))
            elif name == "worker_32":
                new_workers = list(range(1, 33))
            result, status = client.execute_query(actual_query, new_workers)
            # log experiment result
            if result == 'success':
                print "success"
                time = float(status["elapsedNanos"]) / client.NANO_IN_ONE_SEC
                writer.writerow(
                    [name, status["queryId"], time,
                     algebra, profile, output_name, result])
            else:
                print "error"
                writer.writerow(
                    [name, "N.A.", "N.A.", algebra,
                     profile, output_name, result])


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

small_set_queries = [
    (queries.triangle, 'triangle'),
    (queries.fb_q1, 'fb_q1'),
    (queries.clique, 'clique'),
    (queries.fb_q1, 'fb_q1')
]

only_q5 = [
    (queries.fb_q5, 'fb_q5'),
]

rect_query = [
    (queries.rectangle, 'rectangle'),
]

phys_algebras = [
    ('RS_HJ',),
    ('HC_HJ',),
    ('BR_HJ',),
    ('RS_LFJ',),
    ('HC_LFJ',),
    ('BR_LFJ',)
]

phys_algebra_without_rs_lfj = [
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
        languages, phys_algebras, profilingModes, small_set_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment("resource_exp_3_aug.csv", exp_queries)


# experiment 2: profile query execution only
def profile_exp():
    profilingModes = [('QUERY',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, small_set_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment("profile_exp_3_aug.csv", exp_queries)


# experiment 3: cold cache experiment
def cold_cache_exp(filename):
    profilingModes = [('NONE',)]
    exp_queries = itertools.product(
        languages, phys_algebra_without_rs_lfj, profilingModes, rect_query)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


# experiment 4: regular shuffle with leapfrog join
def cold_cache_rslfj_exp(filename):
    profilingModes = [('NONE',)]
    phys_algebras = [('RS_LFJ',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


# experiment 5: rs lfj profile
def profile_rslfj(filename):
    profilingModes = [('QUERY',)]
    phys_algebras = [('RS_LFJ',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


# experiment 6: rs lfj resource
def resource_rslfj(filename):
    profilingModes = [('RESOURCE',)]
    phys_algebras = [('RS_LFJ',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


# experiment 7: scalability queries
def scalability_exp(filename):
    scl_queries = [
        (scalability_queries.worker_8, "worker_8"),
        (scalability_queries.worker_16, "worker_16"),
    ]
    profilingModes = [('NONE',)]
    phys_algebras = [('RS_HJ',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, scl_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    experiment(filename, exp_queries)


def collect_network_data(query_id):
    """collect skew and """
    send = list(client.connection.get_sent_logs(query_id))
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
        # group by destination
        received = sorted(group, key=itemgetter(2))
        received = itertools.groupby(received, key=itemgetter(2))
        r_groups = []
        for r_wid, grp in received:
            r_groups.append([r[3] for r in grp])
        data = [sum(grp) for grp in r_groups]
        skew = max(data)/(sum(data)/64.0)
        # if the data is not significant, ignore it
        if sum(data) < total_num_tuples/64:
            skew = 1
        return skew
    skews = map(compute_skew, groups)
    # return number of tuples being shuffled, and max skew
    print skews
    return total_num_tuples, max(skews)


def add_network_data(query_file, output_file):
    with open(query_file, "rU") as f:
        csvreader = csv.reader(f)
        data = [r for r in csvreader]
        data[0].extend(["shuffled tuples", "max skew"])
        for i, row in enumerate(data):
            if i != 0:
                shuffled_tupels, max_skew = collect_network_data(row[1])
                data[i].extend([shuffled_tupels, max_skew])

    with open(output_file, "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(data)


def collect_resource_data(query_id):
    resource = list(client.connection.get_resource_log(query_id))
    # remove header
    resource = resource[1:]
    # convert numeric fields to long
    # row = [timestamp,opId,measurement,value,queryId,subqueryId,workerId]
    resource = [
        [long(row[0]),
         long(row[1]),
         row[2],
         long(row[3]),
         long(row[4]),
         long(row[5]),
         long(row[6])] for row in resource]
    # filter out row with zero value
    resource = filter(lambda row: row[3] != 0, resource)
    # group by opId, measurement and worker
    resource = sorted(resource, key=itemgetter(1, 2, 6))
    resource = itertools.groupby(resource, key=itemgetter(1, 2, 6))
    groups = []
    for key, grp in resource:
        groups.append([row for row in grp])
    resource = [max(grp, key=itemgetter(0)) for grp in groups]
    # store processed raw data as csv
    with open("query_{}_resource.csv".format(query_id), "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["opId", "measure", "value", "queryId", "workerId"])
        for row in resource:
            csvwriter.writerow([row[1], row[2], row[3], row[4], row[6]])
    # group by measurement
    resource = sorted(resource, key=itemgetter(2))
    resource = itertools.groupby(resource, key=itemgetter(2))
    groups = []
    for key, grp in resource:
        groups.append([row for row in grp])
    result = []
    for grp in groups:
        values = [row[3] for row in grp]
        result.append([grp[0][2], sum(values)])
    cpu, hash_table_size = 0, 0
    for measure, value in result:
        if measure == 'cpuTotal':
            cpu = value
        elif measure == 'hashTableSize':
            hash_table_size = value
    return cpu, hash_table_size


def add_resource_data(query_file, output_file):
    with open(query_file, "rU") as f:
        csvreader = csv.reader(f)
        data = [r for r in csvreader]
        data[0].extend(["cpu time", "hash table size"])
        for i, row in enumerate(data):
            if i != 0:
                cpu, ht_size = collect_resource_data(row[1])
                data[i].extend([cpu, ht_size])

    with open(output_file, "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(data)


def get_output_skew(table_name):
    stored_count_table_name = "cnt_{}".format(table_name)
    query = """
    R = scan({});
    output = [from R emit count(*) as cnt, worker_id() as worker];
    store(output, {});
    """.format(table_name, stored_count_table_name)
    result, status = client.execute_query(
        ('myrial', 'RS_HJ', 'NONE', query, 'get_skew'))
    if result == 'success':
        print "success"
        rel_key = {
            'userName': 'public',
            'programName': 'adhoc',
            'relationName': stored_count_table_name
        }
        tpl_cnts = client.connection.download_dataset(rel_key)
        tpl_cnts = [long(entry['cnt']) for entry in tpl_cnts]
        skew = max(tpl_cnts) / (sum(tpl_cnts) / float(num_servers))
        return skew
    else:
        print "error"
        raise Exception(status)


if __name__ == '__main__':
    scalability_exp("scalability_extrac.csv")
    #cold_cache_exp("cold_cache_rect_2.csv")
    #cold_cache_exp("cold_cache_rect_3.csv")
    #cold_cache_exp("cold_cache_rect_4.csv")
    #cold_cache_exp("cold_cache_rect_5.csv")
    #resource_exp()
    #profile_exp()
    #print get_output_skew('rect_e5_skew')
    # add_network_data(
    #    "/Users/chushumo/Project/papers/2014-multiwayjoin/profile_rslfj.csv",
    #    "profile_rslfj_extend_30_july.csv")
    #add_network_data(
    #    "/Users/chushumo/Project/papers/2014-multiwayjoin/profile_exp.csv",
    #    "profile_extend_30_july.csv")
