import client
import json
import csv

hostname = "dbserver02.cs.washington.edu"
port = "10032"
client.init_connection(hostname, port)


def scl_exp(log_file_name):
    queries = [
        "triangle_worker_32.json",
        "triangle_worker_16.json",
        "triangle_worker_2.json",
        "triangle_worker_4.json",
        "triangle_worker_8.json"
    ]

    with open(log_file_name, "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["query_id", "time", "success or fail"])
        for query in queries:
            with open(query) as qf:
                json_query = json.load(qf)
            if query == "triangle_worker_2.json":
                workers = [1, 2]
            elif query == "triangle_worker_4.json":
                workers = list(range(1, 5))
            elif query == "triangle_worker_8.json":
                workers = list(range(1, 9))
            elif query == "triangle_worker_16.json":
                workers = list(range(1, 17))
            elif query == "triangle_worker_32.json":
                workers = list(range(1, 33))
            for fragment in json_query["plan"]["fragments"]:
                fragment["workers"] = workers
            result, status = client.execute_json(json_query)
            # log experiment result
            if result == 'success':
                print "success"
                time = float(status["elapsedNanos"]) / client.NANO_IN_ONE_SEC
                csvwriter.writerow([
                    status["queryId"], time, "success"])
            else:
                print "error"
                csvwriter.writerow(["N.A.", "N.A.", "fail"])


if __name__ == '__main__':
    scl_exp("scl_hc_lfj_1.csv")
