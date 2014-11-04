import json
import copy

plan_boiler_plate = {
    "language": "MyriaL",
    "logicalRa": "logicalRa",
    "rawQuery": "query",
    "plan": {
        "type": "SubQuery",
        "fragments": []
    }
}


def extract_hcs():
    """
        Extract HyperCube shuffle and output hypercube shuffle only plans
    """
    with open("q4.json") as jf:
        q4 = json.load(jf)
    assert q4["language"] == 'MyriaL'

    # get fragments
    fragments = q4["plan"]["fragments"]
    assert len(fragments) == 9

    # store operators by its id
    operators = dict()
    for frag in fragments:
        for op in frag["operators"]:
            new_op = copy.deepcopy(op)
            operators[int(new_op["opId"])] = new_op
            if new_op["opType"] == "LeapFrogJoin":
                lfj = new_op
    stored_hcs_prefix = "q4_hcs_only_"
    order_bys = []

    # extract hcs
    for i, child_id in enumerate(lfj["argChildren"]):
        # extract related operators
        order_by = operators[child_id]
        hcs_consumer = operators[order_by["argChild"]]
        hcs_producer = operators[hcs_consumer["argOperatorId"]]
        scan = operators[hcs_producer["argChild"]]

        # for later usage
        order_bys.append(order_by)

        # construct store operator
        store = {
            "opId": 4,
            "opName": "MyriaStore(hcs_{})".format(i),
            "relationKey": {
                "programName": "adhoc",
                "userName": "public",
                "relationName": "q4_hcs_only_{}".format(i),
            },
            "argOverwriteTable": True,
            "argChild": 3,
            "opType": "DbInsert"
        }

        # link the operators
        order_by["opId"] = 3
        order_by["argChild"] = 2
        hcs_consumer["opId"] = 2
        hcs_consumer["argOperatorId"] = 1
        hcs_producer["opId"] = 1
        hcs_producer["argChild"] = 0
        scan["opId"] = 0

        # construct plan
        plan = copy.deepcopy(plan_boiler_plate)
        frag1 = {
            "operators": [scan, hcs_producer]
        }
        frag2 = {
            "operators": [hcs_consumer, order_by, store]
        }
        plan["rawQuery"] = "hypercube shuffle of q4 - part {}".format(i)
        plan["plan"]["fragments"].append(frag1)
        plan["plan"]["fragments"].append(frag2)

        ofname = "q4_hc_{}.json".format(i)
        print "write to {}".format(ofname)
        with open(ofname, "wb") as ofile:
            json.dump(plan, ofile)

    # get number of relations
    num_rel = len(lfj["argChildren"])

    # add scans and orderbys
    lfj_ops = []
    for i in range(num_rel):
        rel_name = "{}{}".format(stored_hcs_prefix, i)
        scan = {
            "relationKey": {
                "programName": "adhoc",
                "userName": "public",
                "relationName": rel_name
            },
            "opId": i*2,
            "opName": "MyriaScan({})".format(rel_name),
            "opType": "TableScan"
        }
        lfj_ops.append(scan)
        order_by = order_bys[i]
        order_by["opId"] = i * 2 + 1
        order_by["argChild"] = i * 2
        lfj_ops.append(order_by)

    # construct lfj op
    new_lfj = copy.deepcopy(lfj)
    new_lfj['argChildren'] = [i*2+1 for i in range(num_rel)]
    new_lfj['opId'] = num_rel*2
    lfj_ops.append(new_lfj)

    # add sink root at end
    sink_root = {
        "opType": "SinkRoot",
        "argChild": num_rel*2,
        "opName": "SinkRoot",
        "opId": num_rel*2+1
    }
    lfj_ops.append(sink_root)

    plan = copy.deepcopy(plan_boiler_plate)
    plan["rawQuery"] = "Local Tributary Join"
    plan["plan"]["fragments"] = [
        {
            "operators": lfj_ops,
            "workers": [57]
        }
    ]
    ofname = "q4_local_tj.json"
    print "output {}".format(ofname)
    with open(ofname, "wb") as ofile:
        json.dump(plan, ofile)


if __name__ == '__main__':
    extract_hcs()
