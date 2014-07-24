#!/usr/bin/env python

import queries
import requests

from raco.language.myrialang import (MyriaLeftDeepTreeAlgebra,
                                     MyriaHyperCubeAlgebra,
                                     MyriaHyperCubeLeftDeepTreeJoinAlgebra,
                                     MyriaRegularShuffleLeapFrogAlgebra,
                                     MyriaBroadcastLeftDeepTreeJoinAlgebra,
                                     MyriaBroadCastLeapFrogJoinAlgebra,
                                     compile_to_json)
from raco.catalog import Catalog
from raco import scheme
from raco.algebra import DEFAULT_CARDINALITY
from threading import Lock
from raco.myrial import parser as MyrialParser
from raco.myrial import interpreter as MyrialInterpreter

import myria

# We need a (global) lock on the Myrial parser because yacc is not Threadsafe.
# .. see uwescience/datalogcompiler#39
# ..    (https://github.com/uwescience/datalogcompiler/issues/39)
myrial_parser_lock = Lock()
myrial_parser = MyrialParser.Parser()

sleep_time = 1

# a sequence of queries: [(language, query, phys_algebra, profilingMode), ... ]
example_queries = [
    ('MyriaL', queries.two_rings, 'ALL')
    ]

# need to be initiated
connection = None


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


def execute_query(query):
    language, query_str, phys_algebra, profilingMode = query
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
        query_status = connection.execute_query(compiled)
        return query_status
    except myria.MyriaError as e:
        raise Exception(e)
    except requests.ConnectionError as e:
        raise Exception(e)


def init_connection(hostname, port):
    global connection
    connection = myria.MyriaConnection(hostname=hostname, port=port)


if __name__ == '__main__':
    init_connection(hostname='dbserver02.cs.washington.edu', port=10032)
    q1 = ('myrial', queries.triangle, 'RS_HJ', 'NONE')
    execute_query(q1)
