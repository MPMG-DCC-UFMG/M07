from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json
import pandas

from ..elastic import Elastic


@require_http_methods(["GET"])
def get_log_buscas(request):
    user_id = request.GET.get('user_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if user_id == None and start_date == None and end_date != None:
        response = "Error: At least one parameter must be given."
        return JsonResponse({"response": response})

    body = {
        "size": int(Elastic().es.cat.count("log_buscas").split(" ")[2]), # numero de documentos no indice
        "query": {
            "bool" : {
                "must": []
            }
        }
    }
    
    if user_id != None:
        body["query"]["bool"]["must"].append({
            "term": {
                "id_usuario": user_id
            
            }
        })
    
    if start_date != None:
        start_date = int(float(start_date))
        body["query"]["bool"]["must"].append({
            "range": {
                "data_hora": {
                    "gte": start_date
                }
            }
        })

    if end_date != None:
        end_date = float(end_date)
        if end_date - int(end_date) > 0:
            end_date = int(end_date) + 1
        else:
            end_date = int(end_date)
        body["query"]["bool"]["must"].append({
            "range": {
                "data_hora": {
                    "lte": end_date
                }
            }
        })

    elastic_response = Elastic().es.search(index = "log_buscas", body = body)

    data = []
    for hit in elastic_response["hits"]["hits"]:
        d = hit["_source"]
        d["id"] = hit["_id"]
        data.append(d)

    metadata = {
        "end_date": end_date,
        "took" : elastic_response["took"],
        "timed_out": elastic_response["timed_out"],
        "_shards" : elastic_response["_shards"],
        "total": elastic_response["hits"]["total"],
        "num_documents": len(data)
    }
    if user_id != None: metadata["user_id"] = user_id 
    if start_date != None: metadata["start_date"] = start_date 
    if end_date != None: metadata["end_date"] = end_date
    print(end_date)
    response = {
        "data": data,
        "metadata": metadata

    }
    print(json.dumps(response, indent=" "))
    
    return JsonResponse({"response": response})










# @require_http_methods(["GET"])
# def searches_from_period(request):
#     start_date = request.GET['start_date']
#     end_date = request.GET['end_date']

#     start_date = int(float(start_date))
#     end_date = float(end_date)
#     if end_date - int(end_date) >= 0.5:
#         end_date = int(end_date) + 1
#     else:
#         end_date = int(end_date)

#     elastic_response = Elastic().es.search(index = "log_buscas",\
#         body = {
#             "query": {
#                 "range" : {
#                     "data_hora" : {
#                         "gte" : start_date,
#                         "lt" :  end_date
#                     }
#                 }
#             }
#         })
    
#     data = []
#     for hit in elastic_response["hits"]["hits"]:
#         d = hit["_source"]
#         d["id"] = hit["_id"]
#         data.append(d)

#     metadata = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "took" : elastic_response["took"],
#         "timed_out": elastic_response["timed_out"],
#         "_shards" : elastic_response["_shards"],
#         "total": elastic_response["hits"]["total"]
#     }

#     response = {
#         "data": data,
#         "metadata": metadata

#     }

#     return JsonResponse({"response": response})








# @require_http_methods(["GET"])
# def clicks_per_document(request):
#     size = request.GET['size']

#     response = Elastic().es.search(index = "log_clicks", _source = False,\
#         body = {
#             "aggs" : {
#                "clicks_per_id_documento" : {
#                     "terms" : { "field" : "id_documento.keyword" }
#                 }
#             }
#         })

#     print(json.dumps(response, indent = "  "))

#     return JsonResponse({"response": response})


# @require_http_methods(["GET"])
# def clicks_per_rank_position_hist(request):
#     interval = request.GET['interval']
#     gte = request.GET['gte']
#     lte = request.GET['lte']
    
#     response = Elastic().es.search(index = "log_clicks", _source = False,\
#         body = {
#             "_source": "", 
#             "query": {
#                 "range": {
#                     "posicao": {
#                         "gte": gte,
#                         "lte": lte
#                     }
#                 }
#             }, 
#             "aggs": {
#                 "hist": {
#                     "histogram": {
#                         "field": "posicao",
#                         "interval": interval,
#                         "offset" : 1

#                     }
#                 }
#             }
#         })

#     # print(json.dumps(response, indent = "  "))
    
#     return JsonResponse({"response": response["aggregations"]["hist"]["buckets"]})



# @require_http_methods(["GET"])
# def no_clicks_query(request):
#     response = Elastic().es.search(index = "log_clicks", _source = False,\
#         body = {
#             "_source": "", 
#             "query": {
#                 "range": {
#                     "posicao": {
#                         "lte": lte
#                     }
#                 }
#             }
#         })






# @require_http_methods(["GET"])
# def click_rank_mean(request):

#     response = Elastic().es.search(index = "log_clicks", _source = False,\
#         body = {
#             "aggs" : {
#                "clicks_per_id_documento" : {
#                     "terms" : { "field" : "id_documento.keyword" } 
#                 }
#             }
#         })

#     print(json.dumps(response, indent = "  "))


    # return JsonResponse({"response": response})
