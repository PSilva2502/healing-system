from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from core.decorators import exige_perfil
from core.auditoria import registrar_auditoria
from consultas.models import Consulta, Atendimento
from consultas.forms import (
    FormularioAgendamento, FormularioAgendamentoAdmin, FormularioAtendimento,
)


class ListarConsultasView(LoginRequiredMixin, TemplateView):
    template_name = 'consultas/listar_consultas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        status_filtro = self.request.GET.get('status', '')
        data_filtro = self.request.GET.get('data', '')
        medico_filtro = self.request.GET.get('medico', '')

        if usuario.perfil == 'medico':
            try:
                consultas = Consulta.objects.filter(medico__usuario=usuario)
            except Exception:
                consultas = Consulta.objects.none()
        else:
            consultas = Consulta.objects.all()

        if status_filtro:
            consultas = consultas.filter(status=status_filtro)
        if data_filtro:
            consultas = consultas.filter(data_consulta=data_filtro)
        if medico_filtro and usuario.perfil in ('admin', 'recepcionista'):
            consultas = consultas.filter(medico__id=medico_filtro)

        ctx['consultas'] = consultas.select_related(
            'paciente', 'medico__usuario'
        ).order_by('data_consulta', 'horario')
        ctx['status_filtro'] = status_filtro
        ctx['data_filtro'] = data_filtro
        ctx['hoje'] = date.today()
        return ctx


class AgendarConsultaView(LoginRequiredMixin, View):
    template_name = 'consultas/form_agendamento.html'

    def _usa_form_admin(self, request):
        return request.user.perfil in ('admin', 'recepcionista')

    def get(self, request):
        if self._usa_form_admin(request):
            form = FormularioAgendamentoAdmin()
        else:
            messages.error(request, 'Sem permissão para agendar consultas.')
            return redirect('painel')
        return render(request, self.template_name, {'form': form, 'titulo': 'Agendar Consulta'})

    def post(self, request):
        if self._usa_form_admin(request):
            form = FormularioAgendamentoAdmin(request.POST)
        else:
            messages.error(request, 'Sem permissão para agendar consultas.')
            return redirect('painel')

        if form.is_valid():
            consulta = form.save()
            registrar_auditoria('consulta', 'INSERT')
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect('listar_consultas')
        return render(request, self.template_name, {'form': form, 'titulo': 'Agendar Consulta'})


class CancelarConsultaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        usuario = request.user

        if usuario.perfil == 'medico' and consulta.medico.usuario != usuario:
            raise PermissionDenied

        if consulta.status != 'agendada':
            messages.error(request, 'Só é possível cancelar consultas agendadas.')
            return redirect('listar_consultas')

        dados_anteriores = {'status': consulta.status}
        consulta.status = 'cancelada'
        consulta.save()
        registrar_auditoria('consulta', 'UPDATE', dados_anteriores)
        messages.success(request, 'Consulta cancelada com sucesso.')
        return redirect('listar_consultas')


@method_decorator(exige_perfil('medico', 'admin'), name='dispatch')
class RegistrarAtendimentoView(LoginRequiredMixin, View):
    template_name = 'consultas/form_atendimento.html'

    def get(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        if request.user.perfil == 'medico' and consulta.medico.usuario != request.user:
            raise PermissionDenied
        if hasattr(consulta, 'atendimento'):
            messages.info(request, 'Atendimento já registrado.')
            return redirect('listar_consultas')
        form = FormularioAtendimento()
        return render(request, self.template_name, {'form': form, 'consulta': consulta})

    def post(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        if request.user.perfil == 'medico' and consulta.medico.usuario != request.user:
            raise PermissionDenied
        form = FormularioAtendimento(request.POST)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.consulta = consulta
            atendimento.save()
            consulta.status = 'realizada'
            consulta.save()
            registrar_auditoria('atendimento', 'INSERT')
            registrar_auditoria('consulta', 'UPDATE', {'status': 'agendada'})
            messages.success(request, 'Atendimento registrado com sucesso!')
            return redirect('listar_consultas')
        return render(request, self.template_name, {'form': form, 'consulta': consulta})
