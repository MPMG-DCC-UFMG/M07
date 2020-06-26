from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..elastic import Elastic


@require_http_methods(["GET"])
def document(request):
    if not request.user.is_authenticated:
        data = {'is_authenticated': False}
        return JsonResponse(data)
    sid = request.GET['sid']
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    elastic = Elastic()
    retrieve_doc = elastic.dsl.Document.get(doc_id, using=elastic.es, index=doc_type)
    document = {
        'id': doc_id,
        'title': retrieve_doc.titulo, 
        'description': 'placeholder description',
        'text': retrieve_doc.conteudo,
        'source': retrieve_doc.fonte,
        'type': doc_type,
        'sid': sid
    }

    data = {
        'is_authenticated': True,
        'document': document
    }
    return JsonResponse(data)