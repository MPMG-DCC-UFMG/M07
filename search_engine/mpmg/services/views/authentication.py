from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        valid_user = serializer.is_valid(raise_exception=False)
        if valid_user:
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_info': {
                    'user_id': user.pk,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                },
            })
        else:
            return Response({
                'token': None,
                'user_info': None,
            }, status=status.HTTP_401_UNAUTHORIZED)


class TokenLogout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'success': 'true'})