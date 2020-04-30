from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..elastic import Elastic


@require_http_methods(["GET"])
def document(request):
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    elastic = Elastic()
    retrieve_doc = elastic.dsl.Document.get(doc_id, using=elastic.es, index='diarios')
    document = {
        'id': doc_id,
        'title': 'placeholder title', 
        'description': 'placeholder description',
        'text': retrieve_doc.conteudo,
        'source': retrieve_doc.fonte,
        'type': 'diario',
    }

    data = {
        'document': document
    }
    return JsonResponse(data)