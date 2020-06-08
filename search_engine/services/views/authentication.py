from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        user_info = {'user_id': request.user.id, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'email': request.user.email}
        data = {'success': True, 'auth_token': request.session.session_key, 'message': '', 'user_info': user_info}
        return JsonResponse(data)
    else:
        data = {'success': False, 'auth_token': None, 'message': 'Usuário ou senha inválidos.', 'user_info': None}
        return JsonResponse(data)


@csrf_exempt
def do_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Você saiu.'})
