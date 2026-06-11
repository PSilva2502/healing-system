from django.contrib import admin
from medicos.models import Medico


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'crm', 'especialidade', 'ativo']
    list_filter = ['especialidade', 'ativo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'crm']
