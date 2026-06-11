from django.urls import path
from consultas.views import (
    ListarConsultasView, AgendarConsultaView, CancelarConsultaView,
    RegistrarAtendimentoView,
)

urlpatterns = [
    path('consultas/', ListarConsultasView.as_view(), name='listar_consultas'),
    path('consultas/nova/', AgendarConsultaView.as_view(), name='agendar_consulta'),
    path('consultas/<int:pk>/cancelar/', CancelarConsultaView.as_view(), name='cancelar_consulta'),
    path('atendimentos/<int:pk>/registrar/', RegistrarAtendimentoView.as_view(), name='registrar_atendimento'),
]
