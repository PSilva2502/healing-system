from django import forms
from pacientes.models import Paciente, Convenio


class FormularioConvenio(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = ['nome', 'desconto_percentual', 'ativo']
        labels = {
            'nome': 'Nome do Convênio',
            'desconto_percentual': 'Desconto (%)',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Unimed'}),
            'desconto_percentual': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class FormularioPaciente(forms.ModelForm):
    consentimento_lgpd = forms.BooleanField(
        required=True,
        label='O paciente autoriza o tratamento dos seus dados pessoais e de saúde, '
              'conforme a LGPD (Lei 13.709/2018), para fins de atendimento clínico.',
    )

    class Meta:
        model = Paciente
        fields = ['nome', 'sobrenome', 'email', 'cpf', 'telefone', 'data_nascimento',
                  'convenio', 'consentimento_lgpd']
        labels = {
            'nome': 'Nome',
            'sobrenome': 'Sobrenome',
            'email': 'E-mail',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'data_nascimento': 'Data de Nascimento',
            'convenio': 'Convênio',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'maxlength': '11'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'placeholder': 'paciente@email.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from pacientes.models import Convenio
        self.fields['convenio'].queryset = Convenio.objects.filter(ativo=True)
        self.fields['convenio'].empty_label = 'Particular (sem convênio)'
        self.fields['convenio'].required = False
        self.fields['convenio'].widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        from django.utils import timezone
        paciente = super().save(commit=False)
        if self.cleaned_data.get('consentimento_lgpd') and not paciente.consentimento_em:
            paciente.consentimento_em = timezone.now()
        if commit:
            paciente.save()
        return paciente

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '').strip().replace('.', '').replace('-', '')
        if len(cpf) != 11 or not cpf.isdigit():
            raise forms.ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
        if not self._validar_digitos_cpf(cpf):
            raise forms.ValidationError('CPF inválido. Verifique os dígitos verificadores.')
        qs = Paciente.objects.filter(cpf=cpf)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este CPF já está cadastrado no sistema.')
        return cpf

    def _validar_digitos_cpf(self, cpf):
        if len(set(cpf)) == 1:
            return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        r1 = (soma * 10 % 11) % 10
        if r1 != int(cpf[9]):
            return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        r2 = (soma * 10 % 11) % 10
        return r2 == int(cpf[10])
