import threading

_usuario_atual = threading.local()


def obter_usuario_atual():
    return getattr(_usuario_atual, 'valor', None)


def registrar_usuario_atual(usuario):
    _usuario_atual.valor = usuario


class MiddlewareAuditoria:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            registrar_usuario_atual(request.user)
        else:
            registrar_usuario_atual(None)
        return self.get_response(request)
