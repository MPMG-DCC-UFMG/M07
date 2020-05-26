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
        data = {'success': True, 'auth_token': request.session.session_key}
        return JsonResponse(data)

    else:
        data = {'success': False, 'auth_token': None}
        return JsonResponse(data)


@csrf_exempt
def do_logout(request):
    logout(request)
    return JsonResponse({'success': True})