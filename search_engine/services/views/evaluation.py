from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json

from ..elastic import Elastic


@require_http_methods(["GET"])
def clicks_per_document(request):
    
    response = Elastic().es.search(index = "log_clicks", _source = False,\
        body = {
            "aggs" : {
               "clicks_per_id_documento" : {
                    "terms" : { "field" : "id_documento.keyword" } 
                }
            }
        })

    # print(json.dumps(response, indent = "  "))

    return JsonResponse({"response": response})


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
