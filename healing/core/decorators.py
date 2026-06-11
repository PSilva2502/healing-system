from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def exige_perfil(*perfis_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('entrar')
            if request.user.perfil not in perfis_permitidos:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador
