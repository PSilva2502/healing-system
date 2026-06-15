from django.urls import path
from pacientes.views import (
    ListarPacientesView, CriarPacienteView, EditarPacienteView,
    ExcluirPacienteView, DetalharPacienteView,
    ListarConveniosView, CriarConvenioView, EditarConvenioView,
)

urlpatterns = [
    path('pacientes/', ListarPacientesView.as_view(), name='listar_pacientes'),
    path('pacientes/novo/', CriarPacienteView.as_view(), name='criar_paciente'),
    path('pacientes/<int:pk>/', DetalharPacienteView.as_view(), name='detalhar_paciente'),
    path('pacientes/<int:pk>/editar/', EditarPacienteView.as_view(), name='editar_paciente'),
    path('pacientes/<int:pk>/excluir/', ExcluirPacienteView.as_view(), name='excluir_paciente'),
    path('convenios/', ListarConveniosView.as_view(), name='listar_convenios'),
    path('convenios/novo/', CriarConvenioView.as_view(), name='criar_convenio'),
    path('convenios/<int:pk>/editar/', EditarConvenioView.as_view(), name='editar_convenio'),
]
