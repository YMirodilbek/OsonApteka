from django.shortcuts import  redirect
from functools import wraps

def is_staff(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return fun(request, *args, **kwargs)
        return redirect( '/')
    return wrapper