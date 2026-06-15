import json
from datetime import date
from django import forms
from consultas.models import Consulta, Atendimento, TipoConsulta, TemplateEspecialidade
from medicos.models import Medico, ESPECIALIDADES
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
        fields = ['medico', 'tipo_consulta', 'data_consulta', 'horario', 'observacoes']
        labels = {
            'medico': 'Médico',
            'tipo_consulta': 'Tipo de Consulta',
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
        self.fields['tipo_consulta'].queryset = TipoConsulta.objects.filter(ativo=True)
        self.fields['tipo_consulta'].empty_label = 'Selecione o tipo'
        self.fields['tipo_consulta'].required = False

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
        fields = ['paciente', 'medico', 'tipo_consulta', 'data_consulta', 'horario', 'observacoes']
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


class FormularioEdicaoConsulta(FormularioAgendamentoAdmin):
    """Edição de consulta pela recepção — sem restrição de data mínima."""

    def clean_data_consulta(self):
        return self.cleaned_data.get('data_consulta')


class FormularioTipoConsulta(forms.ModelForm):
    valor_base = forms.DecimalField(
        label='Valor Base (R$)', max_digits=8, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00'}),
    )
    campos = forms.CharField(
        label='Campos do Prontuário (um por linha)', required=False,
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6,
            'placeholder': 'Pressão Arterial\nFrequência Cardíaca\nResultado ECG\nAusculta'}),
        help_text='Cada linha vira um campo no formulário de atendimento deste tipo.',
    )

    class Meta:
        model = TipoConsulta
        fields = ['nome', 'especialidade', 'ativo']
        labels = {
            'nome': 'Nome do Tipo',
            'especialidade': 'Especialidade',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Avaliação Cardiológica'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Cardiologia'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if inst and inst.pk:
            if hasattr(inst, 'tabela_valor'):
                self.fields['valor_base'].initial = inst.tabela_valor.valor_base
            if inst.campos_extras:
                self.fields['campos'].initial = '\n'.join(
                    c.get('label', '') for c in inst.campos_extras
                )

    def campos_lista(self):
        raw = self.cleaned_data.get('campos', '') or ''
        labels = [l.strip() for l in raw.splitlines() if l.strip()]
        return [{'label': l, 'tipo': 'text'} for l in labels]


class FormularioTemplateEspecialidade(forms.ModelForm):
    campos = forms.CharField(
        label='Campos do Prontuário (um por linha)', required=False,
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 8,
            'placeholder': 'Pressão Arterial\nFrequência Cardíaca\nResultado ECG\nAusculta'}),
        help_text='Cada linha vira um campo no atendimento de médicos desta especialidade.',
    )

    class Meta:
        model = TemplateEspecialidade
        fields = ['especialidade', 'ativo']
        labels = {'especialidade': 'Especialidade', 'ativo': 'Ativo'}
        widgets = {
            'especialidade': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if inst and inst.pk and inst.campos_extras:
            self.fields['campos'].initial = '\n'.join(
                c.get('label', '') for c in inst.campos_extras
            )

    def campos_lista(self):
        raw = self.cleaned_data.get('campos', '') or ''
        labels = [l.strip() for l in raw.splitlines() if l.strip()]
        return [{'label': l, 'tipo': 'text'} for l in labels]
