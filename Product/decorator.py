from django.shortcuts import  redirect
from django.http import JsonResponse
from functools import wraps


def is_staff(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return fun(request, *args, **kwargs)
        return redirect( '/filial/login/')
    return wrapper

def login_required_ajax(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": 401, "message": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper