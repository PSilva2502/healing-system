from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.decorators import exige_perfil
from core.auditoria import registrar_auditoria
from pacientes.models import Paciente
from pacientes.forms import FormularioPaciente


@method_decorator(exige_perfil('admin', 'medico', 'recepcionista'), name='dispatch')
class ListarPacientesView(LoginRequiredMixin, TemplateView):
    template_name = 'pacientes/listar_pacientes.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        busca = self.request.GET.get('busca', '')
        pacientes = Paciente.objects.filter(ativo=True)
        if busca:
            pacientes = pacientes.filter(nome__icontains=busca) | \
                        pacientes.filter(sobrenome__icontains=busca) | \
                        pacientes.filter(cpf__icontains=busca)
        ctx['pacientes'] = pacientes.order_by('nome', 'sobrenome')
        ctx['busca'] = busca
        return ctx


@method_decorator(exige_perfil('admin', 'recepcionista'), name='dispatch')
class CriarPacienteView(LoginRequiredMixin, View):
    template_name = 'pacientes/form_paciente.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': FormularioPaciente(),
            'titulo': 'Novo Paciente',
        })

    def post(self, request):
        form = FormularioPaciente(request.POST)
        if form.is_valid():
            form.save()
            registrar_auditoria('paciente', 'INSERT')
            messages.success(request, 'Paciente cadastrado com sucesso!')
            return redirect('listar_pacientes')
        return render(request, self.template_name, {'form': form, 'titulo': 'Novo Paciente'})


@method_decorator(exige_perfil('admin', 'recepcionista'), name='dispatch')
class EditarPacienteView(LoginRequiredMixin, View):
    template_name = 'pacientes/form_paciente.html'

    def get(self, request, pk):
        paciente = get_object_or_404(Paciente, pk=pk)
        form = FormularioPaciente(instance=paciente)
        return render(request, self.template_name, {
            'form': form,
            'paciente': paciente,
            'titulo': 'Editar Paciente',
        })

    def post(self, request, pk):
        paciente = get_object_or_404(Paciente, pk=pk)
        dados_anteriores = {
            'cpf': paciente.cpf,
            'telefone': paciente.telefone,
            'data_nascimento': str(paciente.data_nascimento),
        }
        form = FormularioPaciente(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            registrar_auditoria('paciente', 'UPDATE', dados_anteriores)
            messages.success(request, 'Paciente atualizado com sucesso!')
            return redirect('listar_pacientes')
        return render(request, self.template_name, {
            'form': form,
            'paciente': paciente,
            'titulo': 'Editar Paciente',
        })


@method_decorator(exige_perfil('admin', 'recepcionista'), name='dispatch')
class ExcluirPacienteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        paciente = get_object_or_404(Paciente, pk=pk)
        dados_anteriores = {
            'id': paciente.pk,
            'cpf': paciente.cpf,
            'nome': str(paciente),
        }
        paciente.ativo = False
        paciente.save()
        registrar_auditoria('paciente', 'DELETE', dados_anteriores)
        messages.success(request, 'Paciente desativado com sucesso.')
        return redirect('listar_pacientes')


@method_decorator(exige_perfil('admin', 'medico', 'recepcionista'), name='dispatch')
class DetalharPacienteView(LoginRequiredMixin, TemplateView):
    template_name = 'pacientes/detalhar_paciente.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        return ctx
