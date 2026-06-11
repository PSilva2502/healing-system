from datetime import date
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from core.forms import FormularioEntrar, FormularioCriarUsuario
from core.models import Usuario, Auditoria
from core.decorators import exige_perfil
from django.utils.decorators import method_decorator


class EntrarView(View):
    template_name = 'core/entrar.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('painel')
        return render(request, self.template_name, {'form': FormularioEntrar()})

    def post(self, request):
        form = FormularioEntrar(request.POST, request=request)
        if form.is_valid():
            login(request, form.obter_usuario())
            return redirect('painel')
        return render(request, self.template_name, {'form': form})


class SairView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('entrar')

    def post(self, request):
        logout(request)
        return redirect('entrar')


class PainelView(LoginRequiredMixin, TemplateView):
    login_url = '/entrar/'

    def get_template_names(self):
        return [f'core/painel_{self.request.user.perfil}.html']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user

        if usuario.perfil == 'recepcionista':
            from consultas.models import Consulta
            from pacientes.models import Paciente
            ctx['consultas_hoje'] = Consulta.objects.filter(
                data_consulta=date.today()
            ).count()
            ctx['agendadas_hoje'] = Consulta.objects.filter(
                data_consulta=date.today(), status='agendada'
            ).count()
            ctx['total_pacientes'] = Paciente.objects.filter(ativo=True).count()
            ctx['proximas_consultas'] = Consulta.objects.filter(
                data_consulta__gte=date.today(), status='agendada'
            ).select_related('paciente', 'medico__usuario').order_by(
                'data_consulta', 'horario'
            )[:8]

        elif usuario.perfil == 'medico':
            from consultas.models import Consulta
            from pacientes.models import Paciente
            ctx['consultas_hoje'] = Consulta.objects.filter(
                medico__usuario=usuario, data_consulta=date.today()
            ).count()
            ctx['agenda_hoje'] = Consulta.objects.filter(
                medico__usuario=usuario,
                data_consulta=date.today(),
                status='agendada'
            ).order_by('horario').select_related('paciente')
            ctx['pacientes_ativos'] = Paciente.objects.filter(
                consulta__medico__usuario=usuario
            ).distinct().count()
            ctx['total_consultas_mes'] = Consulta.objects.filter(
                medico__usuario=usuario,
                data_consulta__month=date.today().month,
                data_consulta__year=date.today().year,
            ).count()

        elif usuario.perfil == 'admin':
            from consultas.models import Consulta
            from pacientes.models import Paciente
            from medicos.models import Medico
            ctx['total_consultas'] = Consulta.objects.count()
            ctx['total_pacientes'] = Paciente.objects.count()
            ctx['total_medicos'] = Medico.objects.count()
            ctx['total_usuarios'] = Usuario.objects.count()
            ctx['consultas_hoje'] = Consulta.objects.filter(
                data_consulta=date.today()
            ).count()
            ctx['ultimas_consultas'] = Consulta.objects.order_by(
                '-data_consulta', '-horario'
            ).select_related('paciente', 'medico__usuario')[:5]

        return ctx


@method_decorator(exige_perfil('admin'), name='dispatch')
class ListarUsuariosView(LoginRequiredMixin, TemplateView):
    template_name = 'core/listar_usuarios.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['usuarios'] = Usuario.objects.all().order_by('first_name')
        return ctx


@method_decorator(exige_perfil('admin'), name='dispatch')
class CriarUsuarioView(LoginRequiredMixin, View):
    template_name = 'core/form_usuario.html'

    def get(self, request):
        return render(request, self.template_name, {'form': FormularioCriarUsuario()})

    def post(self, request):
        form = FormularioCriarUsuario(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('listar_usuarios')
        return render(request, self.template_name, {'form': form})
