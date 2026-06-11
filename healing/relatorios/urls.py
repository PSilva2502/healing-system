from django.urls import path
from relatorios.views import RelatoriosView, AuditoriaView

urlpatterns = [
    path('relatorios/', RelatoriosView.as_view(), name='relatorios'),
    path('auditoria/', AuditoriaView.as_view(), name='auditoria'),
]
