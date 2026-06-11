from django import forms
from medicos.models import Medico, ESPECIALIDADES
from core.models import Usuario


class FormularioCriarMedicoCompleto(forms.Form):
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='E-mail')
    senha = forms.CharField(
        label='Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres'})
    )
    crm = forms.CharField(
        label='CRM',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: CRM/BA 123456'})
    )
    especialidade = forms.ChoiceField(label='Especialidade', choices=ESPECIALIDADES)
    foto = forms.ImageField(label='Foto', required=False)

    def clean_crm(self):
        crm = self.cleaned_data.get('crm', '').strip().upper()
        if Medico.objects.filter(crm=crm).exists():
            raise forms.ValidationError('Este CRM já está cadastrado.')
        return crm

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email


class FormularioMedico(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['crm', 'especialidade', 'foto']
        labels = {
            'crm': 'CRM',
            'especialidade': 'Especialidade',
            'foto': 'Foto',
        }

    def clean_crm(self):
        crm = self.cleaned_data.get('crm', '').strip().upper()
        qs = Medico.objects.filter(crm=crm)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este CRM já está cadastrado.')
        return crm
