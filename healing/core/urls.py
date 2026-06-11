from django.urls import path
from core.views import EntrarView, SairView, PainelView, ListarUsuariosView, CriarUsuarioView

urlpatterns = [
    path('', PainelView.as_view(), name='inicio'),
    path('entrar/', EntrarView.as_view(), name='entrar'),
    path('sair/', SairView.as_view(), name='sair'),
    path('painel/', PainelView.as_view(), name='painel'),
    path('usuarios/', ListarUsuariosView.as_view(), name='listar_usuarios'),
    path('usuarios/novo/', CriarUsuarioView.as_view(), name='criar_usuario'),
]
