from itertools import izip
from django.db import connection


def query_to_dicts(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """
    cursor = connection.cursor() #@UndefinedVariable
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return

def query_to_tuples(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """
    cursor = connection.cursor() #@UndefinedVariable
    cursor.execute(query_string, query_args)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    return


def execute_sql(query_string, *query_args):
    
    cursor = connection.cursor() #@UndefinedVariable
    cursor.execute(query_string, query_args)
    return cursor

def exists(query_string, *query_args):
    
    cursor = execute_sql(query_string, query_args)
    return cursor.fetchone() is not None