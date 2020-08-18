from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mpmg.services.models import *

class DocumentView(APIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self):
        self.searchable_indexes = {}
        for k, v in settings.SEARCHABLE_INDICES.items():
            self.searchable_indexes[k] = eval(v)

    def get(self, request):
        sid = request.GET['sid']
        doc_type = request.GET['doc_type']
        doc_id = request.GET['doc_id']
        
        # instancia a classe apropriada e busca o registro no índice
        index_class = self.searchable_indexes[doc_type]
        document = index_class.get(doc_id)

        data = {
            'document': document
        }

        return Response(data)