from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from core.models import Usuario


class FormularioEntrar(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        })
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self._usuario = None

    def clean(self):
        email = self.cleaned_data.get('email')
        senha = self.cleaned_data.get('senha')
        if email and senha:
            usuario = authenticate(self.request, username=email, password=senha)
            if usuario is None:
                raise forms.ValidationError('E-mail ou senha incorretos.')
            self._usuario = usuario
        return self.cleaned_data

    def obter_usuario(self):
        return self._usuario


class FormularioCriarUsuario(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres'})
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'})
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'perfil']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'perfil': 'Perfil',
        }

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        confirmar = cleaned.get('confirmar_senha')
        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        usuario.set_password(self.cleaned_data['senha'])
        if commit:
            usuario.save()
        return usuario
