from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PERFIS = [
        ('admin', 'Administrador'),
        ('medico', 'Médico'),
        ('recepcionista', 'Recepcionista'),
    ]
    perfil = models.CharField(max_length=14, choices=PERFIS, default='recepcionista')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.get_full_name() or self.email

    def nome_completo(self):
        return self.get_full_name()


class Auditoria(models.Model):
    OPERACOES = [
        ('INSERT', 'Inserção'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
    ]
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name='auditorias'
    )
    tabela_afetada = models.CharField(max_length=50)
    operacao = models.CharField(max_length=10, choices=OPERACOES)
    dados_anteriores = models.JSONField(null=True, blank=True)
    executado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria'
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-executado_em']

    def __str__(self):
        return f'{self.operacao} em {self.tabela_afetada} por {self.usuario}'
