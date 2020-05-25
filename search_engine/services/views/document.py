from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from ..elastic import Elastic


@require_http_methods(["GET"])
def document(request):
    if request.user.is_authenticated:
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
            'auth': True,
        }

        data = {
            'document': document
        }
        return JsonResponse(data)
    else:
        document = {'auth': False}
        data = {
            'document': document
        }
        return JsonResponse(data)