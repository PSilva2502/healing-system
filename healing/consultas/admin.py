from django.contrib import admin
from consultas.models import Consulta, Atendimento


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'data_consulta', 'horario', 'status']
    list_filter = ['status', 'data_consulta']
    search_fields = ['paciente__usuario__first_name', 'medico__usuario__first_name']


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'registrado_em']
    readonly_fields = ['registrado_em']
