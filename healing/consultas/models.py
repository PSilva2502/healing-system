from django.db import models
from pacientes.models import Paciente
from medicos.models import Medico


class Consulta(models.Model):
    STATUS = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='consulta')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='consulta')
    data_consulta = models.DateField()
    horario = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS, default='agendada')
    observacoes = models.TextField(blank=True)

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
            f'{self.paciente.usuario.get_full_name()} com '
            f'Dr(a). {self.medico.usuario.get_full_name()} '
            f'em {self.data_consulta:%d/%m/%Y} às {self.horario:%H:%M}'
        )


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
