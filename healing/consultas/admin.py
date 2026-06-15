from django.contrib import admin
from consultas.models import (
    Consulta, Atendimento, TipoConsulta, TabelaValor, TemplateEspecialidade,
)


@admin.register(TemplateEspecialidade)
class TemplateEspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['especialidade', 'ativo']
    list_filter = ['ativo']


@admin.register(TipoConsulta)
class TipoConsultaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especialidade', 'ativo']
    list_filter = ['ativo', 'especialidade']
    search_fields = ['nome', 'especialidade']


@admin.register(TabelaValor)
class TabelaValorAdmin(admin.ModelAdmin):
    list_display = ['tipo_consulta', 'valor_base']


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'tipo_consulta', 'data_consulta', 'horario', 'status', 'valor_final']
    list_filter = ['status', 'data_consulta', 'tipo_consulta']
    search_fields = ['paciente__nome', 'medico__usuario__first_name']


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'registrado_em']
    readonly_fields = ['registrado_em']
