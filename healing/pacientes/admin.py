from django.contrib import admin
from pacientes.models import Paciente, Convenio


@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'desconto_percentual', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sobrenome', 'cpf', 'telefone', 'data_nascimento', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'sobrenome', 'cpf']
