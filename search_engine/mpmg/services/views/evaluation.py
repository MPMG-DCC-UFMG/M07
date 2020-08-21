from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..metrics import Metrics


class MetricsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        metrics = request.GET.getlist('metrics', [])

        if start_date == None and end_date == None:
            data = {'message': 'Pelo menos uma data deve ser fornecida.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        if start_date >= end_date:
            data = {'message': 'Data inicial deve ser anterior à data final.'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

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
        
        return Response(response)