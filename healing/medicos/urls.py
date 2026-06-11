from django.urls import path
from medicos.views import (
    ListarMedicosView, CriarMedicoView, EditarMedicoView, ExcluirMedicoView,
)

urlpatterns = [
    path('medicos/', ListarMedicosView.as_view(), name='listar_medicos'),
    path('medicos/novo/', CriarMedicoView.as_view(), name='criar_medico'),
    path('medicos/<int:pk>/editar/', EditarMedicoView.as_view(), name='editar_medico'),
    path('medicos/<int:pk>/excluir/', ExcluirMedicoView.as_view(), name='excluir_medico'),
]
