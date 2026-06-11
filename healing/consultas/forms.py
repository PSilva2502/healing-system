import json
from datetime import date
from django import forms
from consultas.models import Consulta, Atendimento
from medicos.models import Medico
from pacientes.models import Paciente


HORARIOS_DISPONIVEIS = [
    ('08:00', '08:00'), ('08:30', '08:30'), ('09:00', '09:00'), ('09:30', '09:30'),
    ('10:00', '10:00'), ('10:30', '10:30'), ('11:00', '11:00'), ('11:30', '11:30'),
    ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'), ('14:30', '14:30'),
    ('15:00', '15:00'), ('15:30', '15:30'), ('16:00', '16:00'), ('16:30', '16:30'),
    ('17:00', '17:00'), ('17:30', '17:30'),
]


class FormularioAgendamento(forms.ModelForm):
    horario = forms.ChoiceField(label='Horário', choices=HORARIOS_DISPONIVEIS)

    class Meta:
        model = Consulta
        fields = ['medico', 'data_consulta', 'horario', 'observacoes']
        labels = {
            'medico': 'Médico',
            'data_consulta': 'Data da Consulta',
            'observacoes': 'Observações',
        }
        widgets = {
            'data_consulta': forms.DateInput(attrs={'type': 'date', 'min': str(date.today())}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.paciente = kwargs.pop('paciente', None)
        especialidade = kwargs.pop('especialidade', None)
        super().__init__(*args, **kwargs)
        qs = Medico.objects.filter(ativo=True).select_related('usuario')
        if especialidade:
            qs = qs.filter(especialidade=especialidade)
        self.fields['medico'].queryset = qs
        self.fields['medico'].empty_label = 'Selecione um médico'

    def clean_data_consulta(self):
        data = self.cleaned_data.get('data_consulta')
        if data and data < date.today():
            raise forms.ValidationError('Não é possível agendar para uma data já passada.')
        return data

    def clean(self):
        cleaned = super().clean()
        medico = cleaned.get('medico')
        data = cleaned.get('data_consulta')
        horario = cleaned.get('horario')
        if medico and data and horario:
            conflito = Consulta.objects.filter(
                medico=medico,
                data_consulta=data,
                horario=horario,
                status='agendada',
            )
            if self.instance.pk:
                conflito = conflito.exclude(pk=self.instance.pk)
            if conflito.exists():
                raise forms.ValidationError('Este horário já está ocupado para o médico selecionado.')
        return cleaned


class FormularioAgendamentoAdmin(FormularioAgendamento):
    class Meta(FormularioAgendamento.Meta):
        fields = ['paciente', 'medico', 'data_consulta', 'horario', 'observacoes']
        labels = {
            **FormularioAgendamento.Meta.labels,
            'paciente': 'Paciente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(ativo=True)
        self.fields['paciente'].empty_label = 'Selecione um paciente'


class FormularioAtendimento(forms.ModelForm):
    # Hidden JSON field — populated by the body-map JavaScript
    locais_dor = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial='[]',
    )

    class Meta:
        model = Atendimento
        fields = ['sintomas', 'locais_dor', 'anamnese', 'diagnostico', 'resultado_exame', 'prescricao']
        labels = {
            'sintomas':        'Sintomas Relatados',
            'anamnese':        'Anamnese',
            'diagnostico':     'Diagnóstico',
            'resultado_exame': 'Resultado de Exames',
            'prescricao':      'Prescrição',
        }
        widgets = {
            'sintomas':        forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descreva os sintomas relatados pelo paciente...'}),
            'anamnese':        forms.Textarea(attrs={'rows': 4, 'placeholder': 'Histórico clínico, queixas principais...'}),
            'diagnostico':     forms.Textarea(attrs={'rows': 4, 'placeholder': 'Diagnóstico clínico, CID se aplicável...'}),
            'resultado_exame': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Resultado de raio-x, exames laboratoriais, imagem...'}),
            'prescricao':      forms.Textarea(attrs={'rows': 4, 'placeholder': 'Medicamentos, doses e orientações...'}),
        }

    def clean_locais_dor(self):
        raw = self.cleaned_data.get('locais_dor') or '[]'
        try:
            result = json.loads(raw)
            return result if isinstance(result, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
