from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from core.decorators import exige_perfil
from core.auditoria import registrar_auditoria
from medicos.models import Medico, ESPECIALIDADES
from medicos.forms import FormularioCriarMedicoCompleto, FormularioMedico
from core.models import Usuario


class ListarMedicosView(LoginRequiredMixin, TemplateView):
    template_name = 'medicos/listar_medicos.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        especialidade = self.request.GET.get('especialidade', '')
        busca = self.request.GET.get('busca', '')
        medicos = Medico.objects.filter(ativo=True).select_related('usuario')
        if especialidade:
            medicos = medicos.filter(especialidade=especialidade)
        if busca:
            medicos = medicos.filter(
                usuario__first_name__icontains=busca
            ) | medicos.filter(
                usuario__last_name__icontains=busca
            )
        ctx['medicos'] = medicos
        ctx['especialidades'] = ESPECIALIDADES
        ctx['especialidade_selecionada'] = especialidade
        ctx['busca'] = busca
        return ctx


@method_decorator(exige_perfil('admin'), name='dispatch')
class CriarMedicoView(LoginRequiredMixin, View):
    template_name = 'medicos/form_medico.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': FormularioCriarMedicoCompleto(),
            'titulo': 'Novo Médico',
        })

    def post(self, request):
        form = FormularioCriarMedicoCompleto(request.POST, request.FILES)
        if form.is_valid():
            dados = form.cleaned_data
            usuario = Usuario.objects.create_user(
                username=dados['email'],
                email=dados['email'],
                password=dados['senha'],
                first_name=dados['first_name'],
                last_name=dados['last_name'],
                perfil='medico',
            )
            medico = Medico(
                usuario=usuario,
                crm=dados['crm'],
                especialidade=dados['especialidade'],
            )
            if dados.get('foto'):
                medico.foto = dados['foto']
            medico.save()
            registrar_auditoria('medico', 'INSERT')
            messages.success(request, 'Médico cadastrado com sucesso!')
            return redirect('listar_medicos')
        return render(request, self.template_name, {'form': form, 'titulo': 'Novo Médico'})


@method_decorator(exige_perfil('admin'), name='dispatch')
class EditarMedicoView(LoginRequiredMixin, View):
    template_name = 'medicos/form_medico.html'

    def get(self, request, pk):
        medico = get_object_or_404(Medico, pk=pk)
        form = FormularioMedico(instance=medico)
        return render(request, self.template_name, {
            'form': form,
            'medico': medico,
            'titulo': 'Editar Médico',
        })

    def post(self, request, pk):
        medico = get_object_or_404(Medico, pk=pk)
        dados_anteriores = {'crm': medico.crm, 'especialidade': medico.especialidade}
        form = FormularioMedico(request.POST, request.FILES, instance=medico)
        if form.is_valid():
            form.save()
            registrar_auditoria('medico', 'UPDATE', dados_anteriores)
            messages.success(request, 'Médico atualizado com sucesso!')
            return redirect('listar_medicos')
        return render(request, self.template_name, {
            'form': form,
            'medico': medico,
            'titulo': 'Editar Médico',
        })


@method_decorator(exige_perfil('admin'), name='dispatch')
class ExcluirMedicoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        medico = get_object_or_404(Medico, pk=pk)
        dados_anteriores = {
            'id': medico.pk,
            'crm': medico.crm,
            'nome': medico.usuario.get_full_name(),
        }
        medico.ativo = False
        medico.save()
        registrar_auditoria('medico', 'DELETE', dados_anteriores)
        messages.success(request, 'Médico desativado com sucesso.')
        return redirect('listar_medicos')
