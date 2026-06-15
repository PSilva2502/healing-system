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
from consultas.models import Consulta, Atendimento, TipoConsulta, TabelaValor
from consultas.forms import (
    FormularioAgendamento, FormularioAgendamentoAdmin, FormularioAtendimento,
    FormularioEdicaoConsulta, FormularioTipoConsulta,
)


@method_decorator(exige_perfil('admin'), name='dispatch')
class ListarTiposConsultaView(LoginRequiredMixin, TemplateView):
    template_name = 'consultas/listar_tipos.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipos'] = TipoConsulta.objects.all().order_by('nome')
        return ctx


@method_decorator(exige_perfil('admin'), name='dispatch')
class CriarTipoConsultaView(LoginRequiredMixin, View):
    template_name = 'consultas/form_tipo.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': FormularioTipoConsulta(), 'titulo': 'Novo Tipo de Consulta',
        })

    def post(self, request):
        form = FormularioTipoConsulta(request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.campos_extras = form.campos_lista()
            tipo.save()
            TabelaValor.objects.update_or_create(
                tipo_consulta=tipo,
                defaults={'valor_base': form.cleaned_data['valor_base']},
            )
            registrar_auditoria('tipo_consulta', 'INSERT')
            messages.success(request, 'Tipo de consulta criado com sucesso!')
            return redirect('listar_tipos_consulta')
        return render(request, self.template_name, {'form': form, 'titulo': 'Novo Tipo de Consulta'})


@method_decorator(exige_perfil('admin'), name='dispatch')
class EditarTipoConsultaView(LoginRequiredMixin, View):
    template_name = 'consultas/form_tipo.html'

    def get(self, request, pk):
        tipo = get_object_or_404(TipoConsulta, pk=pk)
        return render(request, self.template_name, {
            'form': FormularioTipoConsulta(instance=tipo),
            'tipo': tipo, 'titulo': 'Editar Tipo de Consulta',
        })

    def post(self, request, pk):
        tipo = get_object_or_404(TipoConsulta, pk=pk)
        form = FormularioTipoConsulta(request.POST, instance=tipo)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.campos_extras = form.campos_lista()
            tipo.save()
            TabelaValor.objects.update_or_create(
                tipo_consulta=tipo,
                defaults={'valor_base': form.cleaned_data['valor_base']},
            )
            registrar_auditoria('tipo_consulta', 'UPDATE')
            messages.success(request, 'Tipo de consulta atualizado com sucesso!')
            return redirect('listar_tipos_consulta')
        return render(request, self.template_name, {
            'form': form, 'tipo': tipo, 'titulo': 'Editar Tipo de Consulta',
        })


class ListarConsultasView(LoginRequiredMixin, TemplateView):
    template_name = 'consultas/listar_consultas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        status_filtro = self.request.GET.get('status', '')
        data_filtro = self.request.GET.get('data', '')
        medico_filtro = self.request.GET.get('medico', '')
        hoje = date.today()

        if usuario.perfil == 'medico':
            try:
                base_qs = Consulta.objects.filter(medico__usuario=usuario)
            except Exception:
                base_qs = Consulta.objects.none()
        else:
            base_qs = Consulta.objects.all()

        consultas = base_qs
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
        ctx['hoje'] = hoje
        ctx['consultas_hoje'] = base_qs.filter(
            data_consulta=hoje, status='agendada'
        ).select_related('paciente', 'medico__usuario').order_by('horario')[:10]
        ctx['total_agendadas'] = base_qs.filter(status='agendada').count()
        ctx['total_realizadas'] = base_qs.filter(status='realizada').count()
        ctx['total_canceladas'] = base_qs.filter(status='cancelada').count()
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
            consulta = form.save(commit=False)
            consulta.valor_final = consulta.calcular_valor()
            consulta.save()
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
            return redirect('detalhar_atendimento', pk=consulta.pk)
        form = FormularioAtendimento()
        return render(request, self.template_name, {
            'form': form, 'consulta': consulta,
            'campos_extras': self._campos_extras(consulta),
        })

    def _campos_extras(self, consulta):
        if consulta.tipo_consulta:
            return consulta.tipo_consulta.campos_extras or []
        return []

    def post(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        if request.user.perfil == 'medico' and consulta.medico.usuario != request.user:
            raise PermissionDenied
        form = FormularioAtendimento(request.POST)
        if form.is_valid():
            atendimento = form.save(commit=False)
            atendimento.consulta = consulta
            atendimento.save()
            # Campos do template clínico → dados_extras na consulta
            campos = self._campos_extras(consulta)
            dados = {}
            for i, campo in enumerate(campos):
                label = campo.get('label', f'campo_{i}')
                dados[label] = request.POST.get(f'extra_{i}', '').strip()
            consulta.dados_extras = dados
            consulta.status = 'realizada'
            consulta.save()
            registrar_auditoria('atendimento', 'INSERT')
            registrar_auditoria('consulta', 'UPDATE', {'status': 'agendada'})
            messages.success(request, 'Atendimento registrado com sucesso!')
            return redirect('detalhar_atendimento', pk=consulta.pk)
        return render(request, self.template_name, {
            'form': form, 'consulta': consulta,
            'campos_extras': self._campos_extras(consulta),
        })


class DetalharAtendimentoView(LoginRequiredMixin, View):
    template_name = 'consultas/detalhar_atendimento.html'

    def get(self, request, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        if request.user.perfil == 'medico' and consulta.medico.usuario != request.user:
            raise PermissionDenied
        if not hasattr(consulta, 'atendimento'):
            messages.error(request, 'Esta consulta não possui atendimento registrado.')
            return redirect('listar_consultas')
        return render(request, self.template_name, {
            'consulta': consulta,
            'atendimento': consulta.atendimento,
        })


@method_decorator(exige_perfil('admin', 'recepcionista'), name='dispatch')
class EditarConsultaView(LoginRequiredMixin, View):
    template_name = 'consultas/form_edicao_consulta.html'

    def _get_consulta_editavel(self, pk):
        consulta = get_object_or_404(Consulta, pk=pk)
        if consulta.status == 'cancelada':
            return consulta, False
        return consulta, True

    def get(self, request, pk):
        consulta, editavel = self._get_consulta_editavel(pk)
        if not editavel:
            messages.error(request, 'Consultas canceladas não podem ser editadas.')
            return redirect('listar_consultas')
        form = FormularioEdicaoConsulta(instance=consulta)
        return render(request, self.template_name, {'form': form, 'consulta': consulta})

    def post(self, request, pk):
        consulta, editavel = self._get_consulta_editavel(pk)
        if not editavel:
            messages.error(request, 'Consultas canceladas não podem ser editadas.')
            return redirect('listar_consultas')
        dados_anteriores = {
            'paciente': str(consulta.paciente),
            'medico': str(consulta.medico),
            'data_consulta': str(consulta.data_consulta),
            'horario': consulta.horario,
        }
        form = FormularioEdicaoConsulta(request.POST, instance=consulta)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.valor_final = consulta.calcular_valor()
            consulta.save()
            registrar_auditoria('consulta', 'UPDATE', dados_anteriores)
            messages.success(request, 'Consulta atualizada com sucesso!')
            return redirect('listar_consultas')
        return render(request, self.template_name, {'form': form, 'consulta': consulta})
