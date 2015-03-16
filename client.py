#!/usr/bin/env python

import requests

from raco.language.myrialang import *
from raco.catalog import Catalog
from raco import scheme
from raco.algebra import DEFAULT_CARDINALITY
from threading import Lock
from raco.myrial import parser as MyrialParser
from raco.myrial import interpreter as MyrialInterpreter
from raco.relation_key import RelationKey
from raco import expression
from raco.expression import UnnamedAttributeRef
from raco import types

import myria
import json

nar = UnnamedAttributeRef


def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ':'))

# We need a (global) lock on the Myrial parser because yacc is not Threadsafe.
# .. see uwescience/datalogcompiler#39
# ..    (https://github.com/uwescience/datalogcompiler/issues/39)
myrial_parser_lock = Lock()
myrial_parser = MyrialParser.Parser()

# need to be initiated
connection = None

# constants
NANO_IN_ONE_SEC = 1000000000


def get_plan(query, language, plan_type, connection,
             phys_algebra=MyriaLeftDeepTreeAlgebra()):
    # only support MyriaL
    assert language == "myrial"

    # We need a (global) lock on the Myrial parser because yacc
    # .. is not Threadsafe and App Engine uses multiple threads.
    with myrial_parser_lock:
        parsed = myrial_parser.parse(query)
    processor = MyrialInterpreter.StatementProcessor(
        MyriaCatalog(connection))
    processor.evaluate(parsed)
    if plan_type == 'logical':
        return processor.get_logical_plan()
    elif plan_type == 'physical':
        return processor.get_physical_plan(phys_algebra)
    else:
        raise NotImplementedError('Myria plan type %s' % plan_type)


def get_physical_algebra(phys_algebra_str, connection):
    catalog = MyriaCatalog(connection)
    # return corresponding physical algebra
    if(phys_algebra_str == 'RS_HJ'):
        return MyriaLeftDeepTreeAlgebra()
    elif(phys_algebra_str == 'HC_HJ'):
        return MyriaHyperCubeLeftDeepTreeJoinAlgebra(catalog)
    elif(phys_algebra_str == 'BR_HJ'):
        return MyriaBroadcastLeftDeepTreeJoinAlgebra(catalog)
    elif(phys_algebra_str == 'RS_LFJ'):
        return MyriaRegularShuffleLeapFrogAlgebra()
    elif(phys_algebra_str == 'HC_LFJ'):
        return MyriaHyperCubeAlgebra(catalog)
    elif(phys_algebra_str == 'BR_LFJ'):
        return MyriaBroadCastLeapFrogJoinAlgebra(catalog)
    else:
        raise ValueError("{} is not valid.".format(phys_algebra_str))


class MyriaCatalog(Catalog):

    def __init__(self, connection):
        self.connection = connection

    def get_scheme(self, rel_key):
        relation_args = {
            'userName': rel_key.user,
            'programName': rel_key.program,
            'relationName': rel_key.relation
        }
        if not self.connection:
            raise RuntimeError(
                "no schema for relation %s because no connection" % rel_key)
        try:
            dataset_info = self.connection.dataset(relation_args)
        except myria.MyriaError:
            raise ValueError('No relation {} in the catalog'.format(rel_key))
        schema = dataset_info['schema']
        return scheme.Scheme(zip(schema['columnNames'], schema['columnTypes']))

    def get_num_servers(self):
        if not self.connection:
            raise RuntimeError("no connection.")
        return len(self.connection.workers_alive())

    def num_tuples(self, rel_key):
        relation_args = {
            'userName': rel_key.user,
            'programName': rel_key.program,
            'relationName': rel_key.relation
        }
        if not self.connection:
            raise RuntimeError(
                "no cardinality of %s because no connection" % rel_key)
        try:
            dataset_info = self.connection.dataset(relation_args)
        except myria.MyriaError:
            raise ValueError(rel_key)
        num_tuples = dataset_info['numTuples']
        assert type(num_tuples) is int
        # that's a work round. numTuples is -1 if the dataset is old
        if num_tuples != -1:
            assert num_tuples >= 0
            return num_tuples
        return DEFAULT_CARDINALITY


def execute_query(query, workers="ALL"):
    """
    query - (language, phyiscal_algebra, profiling_mode, query_str, query_name)
    """
    language, phys_algebra, profilingMode, query_str, query_name = query
    print "executing query {}".format(query_name)
    if connection is None:
        raise Exception("connection is not initiated.")
    physical_algebra = get_physical_algebra(phys_algebra, connection)
    try:
        # Generate logical plan
        logical_plan = get_plan(
            query_str, language, "logical", connection, physical_algebra)
        # Generate physical plan
        physical_plan = get_plan(
            query_str, language, "physical", connection, physical_algebra)
        # compile to json
        compiled = compile_to_json(
            query_str, logical_plan, physical_plan, language)
        compiled['profilingMode'] = profilingMode
        if workers != "ALL":
            for fragment in compiled["plan"]["fragments"]:
                fragment["workers"] = workers
        # execute the query util it is finished (or errored)
        query_status = connection.execute_query(compiled)
        if query_status["status"] == 'SUCCESS':
            return 'success', query_status
        else:
            return query_status["status"], query_status
    except myria.MyriaError as e:
        print "myrial error: {}".format(e)
        return 'fail', 'MyriaError'
    except requests.ConnectionError as e:
        print e
        return 'fail', 'ConnectionError'


def execute_json(json_query):
    """
    Execute json query.
    Argument:
        json_query - json query
    """
    # check connections
    if connection is None:
        raise Exception("connection is not initiated.")
    try:
        # execute the query util it is finished (or errored)
        query_status = connection.execute_query(json_query)
        if query_status["status"] == 'SUCCESS':
            return 'success', query_status
        else:
            return query_status["status"], query_status
    except myria.MyriaError as e:
        print "myrial error: {}".format(e)
        return 'fail', 'MyriaError'
    except requests.ConnectionError as e:
        print e
        return 'fail', 'ConnectionError'


def execute_physical_plan(phys_str, logical_plan="LP", raw_query='query'):
    """
    Execute physical plan
    Argument:
        phys_str: physical plan string
    """
    physical_plan = eval(phys_str)
    json_plan = compile_to_json(
        str(raw_query), str(logical_plan), physical_plan)
    json_plan["profilingMode"] = "QUERY"
    print pretty_json(json_plan)
    return execute_json(json_plan)


def init_connection(hostname, port):
    global connection
    connection = myria.MyriaConnection(hostname=hostname, port=port)
