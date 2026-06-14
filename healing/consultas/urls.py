from django.urls import path
from consultas.views import (
    ListarConsultasView, AgendarConsultaView, CancelarConsultaView,
    RegistrarAtendimentoView, DetalharAtendimentoView, EditarConsultaView,
)

urlpatterns = [
    path('consultas/', ListarConsultasView.as_view(), name='listar_consultas'),
    path('consultas/nova/', AgendarConsultaView.as_view(), name='agendar_consulta'),
    path('consultas/<int:pk>/cancelar/', CancelarConsultaView.as_view(), name='cancelar_consulta'),
    path('consultas/<int:pk>/editar/', EditarConsultaView.as_view(), name='editar_consulta'),
    path('atendimentos/<int:pk>/registrar/', RegistrarAtendimentoView.as_view(), name='registrar_atendimento'),
    path('atendimentos/<int:pk>/', DetalharAtendimentoView.as_view(), name='detalhar_atendimento'),
]
