import client
import json

hostname = "dbserver02.cs.washington.edu"
port = "10032"
num_servers = 64

client.init_connection(hostname, port)


def hypercube_shuffle():
    """
    Only hypercube shuffle
    """
    json_query_files = [
        "q1_hc_1.json", "q1_hc_2.json", "q1_hc_3.json", "q1_hc_4.json",
        "q1_hc_5.json", "q1_hc_6.json", "q1_hc_7.json", "q1_hc_8.json"]
    for query_file_path in json_query_files:
        with open(query_file_path) as jf:
            query = json.load(jf)
            print "executing query {}".format(query_file_path)
            client.execute_json(query)


if __name__ == '__main__':
    hypercube_shuffle()
