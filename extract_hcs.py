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

    # extract hcs
    for i, child_id in enumerate(lfj["argChildren"]):
        # extract related operators
        order_by = operators[child_id]
        hcs_consumer = operators[order_by["argChild"]]
        hcs_producer = operators[hcs_consumer["argOperatorId"]]
        scan = operators[hcs_producer["argChild"]]

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


if __name__ == '__main__':
    extract_hcs()
