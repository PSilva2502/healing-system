from datetime import date
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from core.decorators import exige_perfil
from core.models import Auditoria
from consultas.models import Consulta
from pacientes.models import Paciente
from medicos.models import Medico


@method_decorator(exige_perfil('admin'), name='dispatch')
class RelatoriosView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorios.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = date.today()
        ctx['total_consultas'] = Consulta.objects.count()
        ctx['consultas_agendadas'] = Consulta.objects.filter(status='agendada').count()
        ctx['consultas_realizadas'] = Consulta.objects.filter(status='realizada').count()
        ctx['consultas_canceladas'] = Consulta.objects.filter(status='cancelada').count()
        ctx['consultas_hoje'] = Consulta.objects.filter(data_consulta=hoje).count()
        ctx['total_pacientes'] = Paciente.objects.filter(ativo=True).count()
        ctx['total_medicos'] = Medico.objects.filter(ativo=True).count()
        ctx['consultas_mes'] = Consulta.objects.filter(
            data_consulta__month=hoje.month,
            data_consulta__year=hoje.year,
        ).count()

        # ── Financeiro ──────────────────────────────────────
        realizadas = Consulta.objects.filter(status='realizada')
        ctx['receita_total'] = realizadas.aggregate(t=Sum('valor_final'))['t'] or 0
        ctx['receita_prevista'] = Consulta.objects.filter(
            status='agendada'
        ).aggregate(t=Sum('valor_final'))['t'] or 0
        ctx['receita_mes'] = realizadas.filter(
            data_consulta__month=hoje.month, data_consulta__year=hoje.year,
        ).aggregate(t=Sum('valor_final'))['t'] or 0

        # Receita por médico
        ctx['receita_por_medico'] = realizadas.values(
            'medico__usuario__first_name', 'medico__usuario__last_name',
        ).annotate(
            total=Sum('valor_final'), qtd=Count('id'),
        ).order_by('-total')

        # Receita por especialidade
        ctx['receita_por_especialidade'] = realizadas.values(
            'medico__especialidade',
        ).annotate(
            total=Sum('valor_final'), qtd=Count('id'),
        ).order_by('-total')

        return ctx


@method_decorator(exige_perfil('admin'), name='dispatch')
class AuditoriaView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/auditoria.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tabela = self.request.GET.get('tabela', '')
        operacao = self.request.GET.get('operacao', '')
        registros = Auditoria.objects.select_related('usuario').order_by('-executado_em')
        if tabela:
            registros = registros.filter(tabela_afetada=tabela)
        if operacao:
            registros = registros.filter(operacao=operacao)
        ctx['registros'] = registros[:100]
        ctx['tabela_filtro'] = tabela
        ctx['operacao_filtro'] = operacao
        ctx['tabelas'] = Auditoria.objects.values_list(
            'tabela_afetada', flat=True
        ).distinct()
        return ctx
