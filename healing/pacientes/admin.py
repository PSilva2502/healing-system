from django.contrib import admin
from pacientes.models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sobrenome', 'cpf', 'telefone', 'data_nascimento', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'sobrenome', 'cpf']
