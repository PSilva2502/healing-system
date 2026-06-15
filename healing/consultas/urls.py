from django.urls import path
from consultas.views import (
    ListarConsultasView, AgendarConsultaView, CancelarConsultaView,
    RegistrarAtendimentoView, DetalharAtendimentoView, EditarConsultaView,
    ListarTiposConsultaView, CriarTipoConsultaView, EditarTipoConsultaView,
    ExcluirTipoConsultaView,
    ListarTemplatesView, CriarTemplateView, EditarTemplateView, ExcluirTemplateView,
)

urlpatterns = [
    path('consultas/', ListarConsultasView.as_view(), name='listar_consultas'),
    path('consultas/nova/', AgendarConsultaView.as_view(), name='agendar_consulta'),
    path('consultas/<int:pk>/cancelar/', CancelarConsultaView.as_view(), name='cancelar_consulta'),
    path('consultas/<int:pk>/editar/', EditarConsultaView.as_view(), name='editar_consulta'),
    path('atendimentos/<int:pk>/registrar/', RegistrarAtendimentoView.as_view(), name='registrar_atendimento'),
    path('atendimentos/<int:pk>/', DetalharAtendimentoView.as_view(), name='detalhar_atendimento'),
    path('tipos-consulta/', ListarTiposConsultaView.as_view(), name='listar_tipos_consulta'),
    path('tipos-consulta/novo/', CriarTipoConsultaView.as_view(), name='criar_tipo_consulta'),
    path('tipos-consulta/<int:pk>/editar/', EditarTipoConsultaView.as_view(), name='editar_tipo_consulta'),
    path('tipos-consulta/<int:pk>/excluir/', ExcluirTipoConsultaView.as_view(), name='excluir_tipo_consulta'),
    path('templates/', ListarTemplatesView.as_view(), name='listar_templates'),
    path('templates/novo/', CriarTemplateView.as_view(), name='criar_template'),
    path('templates/<int:pk>/editar/', EditarTemplateView.as_view(), name='editar_template'),
    path('templates/<int:pk>/excluir/', ExcluirTemplateView.as_view(), name='excluir_template'),
]
