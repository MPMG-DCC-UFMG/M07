import csv
import ctypes
import os
import time
import json

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from os import listdir
from os.path import isfile, join


def list_files(path):
    """
    List all files from a given folder
    """
    if path[-1] != "/":
        path = path+"/"
    return [path+f for f in listdir(path) if isfile(join(path, f))]


class Indexer:
    
    def __init__(self, elastic_address = 'localhost:9200'):

        self.ELASTIC_ADDRESS = elastic_address
        self.es = Elasticsearch([self.ELASTIC_ADDRESS], timeout=120, max_retries=3, retry_on_timeout=True)

        csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

    def generate_formated_csv_lines(self, file_path, index, encoding="utf8"):
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
                if line[field]!= '':
                    doc[field] = line[field]
            
            yield {
                "_index": index,
                "_source": doc
            }

    def simple_indexer(self, files_to_index, index):
        """
        Index the csvs files using helpers.bulk
        """
        start = time.time()

        responses = {}
        for csv_file in files_to_index:
            print("Indexing: " + csv_file)
            responses[csv_file] =  helpers.bulk(self.es, self.generate_formated_csv_lines(csv_file, index) )
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
        
        error = False
        for csv_file in files_to_index:
            try:
                print("Indexing: " + csv_file + "...")
                for success, info in helpers.parallel_bulk(self.es, self.generate_formated_csv_lines(csv_file, index), thread_count = thread_count, queue_size = thread_count): 
                    if not success:
                        print("Detected error while indexing: " + csv_file)
                        error = True
                        print(info)
            except:
                error = True
                print("Detected error while indexing: " + csv_file)
        
        if not error:
            print("All files indexed with no error.")
            end = time.time()
            print("Indexing time: {:.4f} seconds.".format(end-start))
        else:
            print("Error while indexing.")

