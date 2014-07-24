#!/usr/bin/env python

import queries
import requests
import csv
import itertools

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


def execute_query(query):
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
        # execute the query util it is finished (or errored)
        query_status = connection.execute_query(compiled)
        return 'success', query_status
    except myria.MyriaError as e:
        print e
        return 'fail', 'MyriaError'
    except requests.ConnectionError as e:
        print e
        return 'fail', 'ConnectionError'


def init_connection(hostname, port):
    global connection
    connection = myria.MyriaConnection(hostname=hostname, port=port)


def experiment(filename):
    exp_raw_queries = [
        (queries.triangle, 'triangle'),
        (queries.fb_q1, 'fb_q1'),
        (queries.rectangle, 'rectangle'),
        (queries.fb_q2, 'fb_q2'),
        (queries.cocktail, 'cocktail'),
        (queries.fb_q3, 'fb_q3'),
        (queries.clique, 'clique'),
        (queries.fb_q4, 'fb_q4')
    ]
    profilingModes = [('ALL',)]
    phys_algebras = [
        ('RS_HJ',),
        ('HC_HJ',),
        ('BR_HJ',),
        ('RS_LFJ',),
        ('HC_LFJ',),
        ('BR_LFJ',)
    ]
    languages = [('myrial',)]
    exp_queries = itertools.product(
        languages, phys_algebras, profilingModes, exp_raw_queries)
    exp_queries = [
        reduce(lambda t1, t2: t1 + t2, query) for query in exp_queries]
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["name", "qid", "time", "algebra", "profilingMode", "success"])
        for query in exp_queries:
            # submit queries
            result, status = execute_query(query)
            _, algebra, profie, _, name = query
            # log experiment result
            if result == 'fail':
                writer.writerow(
                    [name, "N.A.", "N.A.", algebra, profie, "NO"])
            elif result == 'success':
                time = float(status["elapsedNanos"]) / NANO_IN_ONE_SEC
                writer.writerow(
                    [name, status["queryId"], time, algebra, profie, "YES"])


if __name__ == '__main__':
    init_connection(hostname='dbserver02.cs.washington.edu', port=10032)
    experiment("test.csv")
