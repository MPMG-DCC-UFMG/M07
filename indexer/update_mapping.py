import argparse
import json
import os

import indexer

from elasticsearch import Elasticsearch

def main(args):
    
    force_reindexation = []
    update_settings = []
    if args["force_reindexation"] != None:
        force_reindexation = args["force_reindexation"]
    if args["update_settings"] != None:
        update_settings = args["update_settings"]
    for i in update_settings:
        if i in force_reindexation:
            update_settings.remove(i)

    es = Elasticsearch()
    settings = json.load(open('additional_settings.json'))
    updated_mappings = json.load(open('mappings.json'))
    local_indices = [index for index in updated_mappings.keys() if es.indices.exists(index)]
    local_mappings = es.indices.get_mapping(local_indices)
    
    csv_indexer = indexer.Indexer()
    for index in updated_mappings.keys():
        print("Checking " + index + "...")

        if not os.path.isdir(index):
                os.mkdir(index)
                print("Created new directory: " + index)
        
        # se o indice ja existe e o mapping eh diferente ou se esta na lista de force_reindexation
        if (index in local_indices and local_mappings[index] != updated_mappings[index]) or (index in force_reindexation and index in local_indices): 
            es.indices.delete(index)
            print("Existing index deleted: " + index)
            local_indices.remove(index)
        
        if index not in local_indices: # caso o indice ainda nao exista ou foi excluido
            es.indices.create(index, body = updated_mappings[index] ) # cria indice
            es.indices.put_settings(index = index, body = settings[index]["settings"]) # atualiza settings
            print("New index created: " + index)
            files_to_index = indexer.list_files(index)
            if len(files_to_index) == 0:
                print("No files to index in " + index)
            else:
                print("Indexing " + str(len(files_to_index)) + " files in " + index)
                csv_indexer.parallel_indexer(files_to_index, index, thread_count=4) # insere documentos
        
        if index in update_settings:
            if index in settings:
                es.indices.put_settings(index = index, body = settings[index]["settings"]) # atualiza settings
                print("Updated settings from " + index)
            else:
                print("There is no settings to update in " + index)

        print()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Verifica se o indice sofreu alguma alteracao e, nesse caso,\
    cria o indice novamente com o dado mapping. Força update dos settings dos dados indices.')
    
    parser.add_argument("-force_reindexation", nargs='+', help="List of indices to force reindexation")
    parser.add_argument("-update_settings", nargs='+', help="List of indices to force settings update")

    # Get all args
    args = vars(parser.parse_args())

    main(args)
