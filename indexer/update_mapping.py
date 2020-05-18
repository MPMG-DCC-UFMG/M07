import json
import os

import indexer

from elasticsearch import Elasticsearch


es = Elasticsearch()
updated_mappings = json.load(open('mappings.json'))
local_indices = [index for index in updated_mappings.keys() if es.indices.exists(index)]
local_mappings = es.indices.get_mapping(local_indices)

csv_indexer = indexer.Indexer()
for index in updated_mappings.keys():
    
    if not os.path.isdir(index):
            os.mkdir(index)
            print("Created new directory: " + index)

    if index in local_indices and local_mappings[index] != updated_mappings[index]: # se o indice ja existe e o mapping eh diferente
        es.indices.delete(index)
        print("Existing index deleted: " + index)
        local_indices.remove(index)
    
    if index not in local_indices: # caso o indice ainda nao exista
        es.indices.create(index, body = updated_mappings[index] ) # cria indice
        print("New index created: " + index)
        files_to_index = indexer.list_files(index)
        if len(files_to_index) == 0:
            print("No file to index in " + index)
        else:
            print("Indexing " + str(len(files_to_index)) + " files in " + index)
            csv_indexer.parallel_indexer(files_to_index, index, thread_count=4) # insere documentos
        
