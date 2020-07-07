from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings


@require_http_methods(["GET"])
def document(request):
    if not request.user.is_authenticated:
        data = {'is_authenticated': False}
        return JsonResponse(data)
    
    sid = request.GET['sid']
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    
    # instancia a classe apropriada e busca o registro no índice
    index_class = settings.SEARCHABLE_INDICES[doc_type]
    document = index_class.get(doc_id)

    data = {
        'is_authenticated': True,
        'document': document
    }
    return JsonResponse(data)