from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..metrics import Metrics

@require_http_methods(["GET"])
def get_metrics(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    metrics = request.GET.getlist('metrics', [])

    if start_date == None and end_date == None:
        raise Exception('At leat one date parameter must be given.')

    m = Metrics(start_date=start_date, end_date=end_date)

    callable_funcs = []
    for func in Metrics.__dict__.values():
        if callable(func):
            callable_funcs.append(func.__name__)
    callable_funcs.remove("__init__")
    callable_funcs.remove("_get_logs")

    if metrics == []:
        metrics = callable_funcs
    
    response = {}
    for metric in metrics:
        if metric in callable_funcs:
            response[metric] = getattr(m, metric)()
    
    return JsonResponse(response)






