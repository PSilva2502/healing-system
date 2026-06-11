from django import forms
from pacientes.models import Paciente


class FormularioPaciente(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome', 'sobrenome', 'email', 'cpf', 'telefone', 'data_nascimento']
        labels = {
            'nome': 'Nome',
            'sobrenome': 'Sobrenome',
            'email': 'E-mail',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'data_nascimento': 'Data de Nascimento',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'cpf': forms.TextInput(attrs={'placeholder': '00000000000', 'maxlength': '11'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'placeholder': 'paciente@email.com'}),
        }

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
