from django.db import models
from pacientes.models import Paciente
from medicos.models import Medico


class TipoConsulta(models.Model):
    nome          = models.CharField(max_length=100, verbose_name='Nome')
    especialidade = models.CharField(max_length=100, blank=True, verbose_name='Especialidade')
    campos_extras = models.JSONField(default=list, blank=True,
                      verbose_name='Campos do template',
                      help_text='Lista de campos extras ex: [{"label":"Pressão Arterial","tipo":"text"}]')
    ativo         = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_consulta'
        verbose_name = 'Tipo de Consulta'
        verbose_name_plural = 'Tipos de Consulta'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TabelaValor(models.Model):
    tipo_consulta = models.OneToOneField(TipoConsulta, on_delete=models.CASCADE,
                      related_name='tabela_valor', verbose_name='Tipo de Consulta')
    valor_base    = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor Base (R$)')

    class Meta:
        db_table = 'tabela_valor'
        verbose_name = 'Tabela de Valor'
        verbose_name_plural = 'Tabela de Valores'

    def __str__(self):
        return f'{self.tipo_consulta} — R$ {self.valor_base}'


class Consulta(models.Model):
    STATUS = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]
    paciente      = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='consulta')
    medico        = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='consulta')
    tipo_consulta = models.ForeignKey(TipoConsulta, null=True, blank=True,
                      on_delete=models.SET_NULL, verbose_name='Tipo de Consulta')
    data_consulta = models.DateField()
    horario       = models.TimeField()
    status        = models.CharField(max_length=10, choices=STATUS, default='agendada')
    valor_final   = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                      verbose_name='Valor Final (R$)')
    dados_extras  = models.JSONField(default=dict, blank=True,
                      verbose_name='Dados do Template Clínico')
    observacoes   = models.TextField(blank=True)

    class Meta:
        db_table = 'consulta'
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering = ['-data_consulta', '-horario']
        constraints = [
            models.UniqueConstraint(
                fields=['medico', 'data_consulta', 'horario'],
                condition=models.Q(status='agendada'),
                name='medico_horario_unico',
            )
        ]

    def __str__(self):
        return (
            f'{self.paciente} com '
            f'Dr(a). {self.medico.usuario.get_full_name()} '
            f'em {self.data_consulta:%d/%m/%Y} às {self.horario:%H:%M}'
        )

    def calcular_valor(self):
        """Valor base do tipo menos desconto do convênio do paciente."""
        if not self.tipo_consulta or not hasattr(self.tipo_consulta, 'tabela_valor'):
            return None
        base = self.tipo_consulta.tabela_valor.valor_base
        convenio = getattr(self.paciente, 'convenio', None)
        if convenio and convenio.desconto_percentual:
            from decimal import Decimal
            desconto = base * (convenio.desconto_percentual / Decimal('100'))
            return (base - desconto).quantize(Decimal('0.01'))
        return base


class Atendimento(models.Model):
    consulta      = models.OneToOneField(Consulta, on_delete=models.CASCADE, related_name='atendimento')
    sintomas      = models.TextField(blank=True, default='', verbose_name='Sintomas relatados')
    locais_dor    = models.JSONField(default=list, blank=True, verbose_name='Locais de dor')
    anamnese      = models.TextField()
    diagnostico   = models.TextField()
    resultado_exame = models.TextField(blank=True, default='', verbose_name='Resultado de exames')
    prescricao    = models.TextField(blank=True)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'atendimento'
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'

    def __str__(self):
        return f'Atendimento da consulta #{self.consulta.pk}'
