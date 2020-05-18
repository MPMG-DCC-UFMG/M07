import csv
import ctypes
import os
import argparse
import time
import json

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from os import listdir
from os.path import isfile, join


"""
Functions
"""

def list_files(mypath):
    """
    List all files from a given folder
    """
    if mypath[-1] != "/":
        mypath = mypath+"/"
    return [mypath+f for f in listdir(mypath) if isfile(join(mypath, f))]


def generate_formated_csv_lines(file_path, index_name, encoding="utf8"):
    """
    Generates formated entries to indexed by the bulk API
    """
    file = open(file_path, encoding=encoding)
    table = csv.DictReader(file)
    columns = table.fieldnames.copy()
    
    for line in table:
        line = dict(line)
        doc = {}
        for field in columns:
            doc[field] = line[field]
        
        doc["fonte_csv"] = file_path
    
        yield {
            "_index": index_name,
            "_source": doc
        }



"""

"""

class Indexer:
    def __init__(self):
        config = json.load(open('../config.json'))
        self.ELASTIC_ADDRESS = config['elasticsearch']['host'] + ":" + config['elasticsearch']['port']

    def simple_indexer(self, files_to_index, index):
        """
        Index the csvs files using helpers.bulk
        """
        start = time.time()
       
        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
        es = Elasticsearch([self.ELASTIC_ADDRESS], timeout=30, max_retries=3, retry_on_timeout=True)

        responses = {}
        for csv_file in files_to_index:
            print("Indexing: " + csv_file)
            responses[csv_file] =  helpers.bulk(es, generate_formated_csv_lines(csv_file, index) )
            print("  Response: " + str(responses[csv_file]))

            if len(responses[csv_file][1]) > 0 :
                print("Detected error while indexing: " + csv_file)
            else:
                end = time.time()
                print("Indexing time: {:.4f} seconds.".format(end-start))


    def parallel_indexer(self, files_to_index, index, thread_count):
        """
        Index the csvs files using helpers.parallel_bulk
        Note that the queue_size is the same as thread_count
        """
        start = time.time()

        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))
        es = Elasticsearch([self.ELASTIC_ADDRESS], timeout=30, max_retries=3, retry_on_timeout=True)

        error = False
        for csv_file in files_to_index:
            print("Indexing: " + csv_file + "...")
            for success, info in helpers.parallel_bulk(es, generate_formated_csv_lines(csv_file, index), thread_count = thread_count, queue_size = thread_count): 
                if not success:
                    print("Detected error while indexing: " + csv_file)
                    error = True
                    print(info)
        if not error:
            print("All files indexed with no error.")
            end = time.time()
            print("Indexing time: {:.4f} seconds.".format(end-start))
        else:
            print("Error while indexing.")


"""
Main
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Indexa arquivos csv no ES dado.')

    parser.add_argument("-strategy", choices=['simple', 'parallel'], help="Strategy for indexing the data: [simple] or [parallel]", required=True)
    parser.add_argument("-index", help="Index", required=True)
    parser.add_argument("-f", nargs='+', help="List of csv files to index")
    parser.add_argument("-d", nargs='+', help="List of directories which all files will be indexed")
    parser.add_argument("-t", help="Threadpool size to use for the bulk requests")
    
    # Get all args
    args = vars(parser.parse_args())

    index = args["index"]
    
    files_to_index = []
    if args['f'] != None:
        for f in args['f']:
            if isfile(f):
                files_to_index.append(f)
    if args['d'] != None:
        for folder in args['d']:
            for f in list_files(folder):
                files_to_index.append(f)
    
    if args["strategy"] == "simple" and args['t'] != None:
        print("WARNING: Argument -t (Threadpool size) is not applicable.")
    thread_count = None
    if args["strategy"] == "parallel":
        thread_count = 4
        if args['t'] != None:
            thread_count = int(args['t'])


    # Index all the csv files in the list
    i = Indexer()
    if args['strategy'] == 'simple':
        i.simple_indexer( files_to_index, index)
    elif args['strategy'] == 'parallel':
        i.parallel_indexer(files_to_index, index, thread_count )
