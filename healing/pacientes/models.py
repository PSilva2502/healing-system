from django.db import models


class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'paciente'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nome', 'sobrenome']

    def __str__(self):
        return f'{self.nome} {self.sobrenome}'.strip()

    def nome_completo(self):
        return self.__str__()

    def iniciais(self):
        ini_nome = self.nome[:1].upper() if self.nome else ''
        ini_sob = self.sobrenome[:1].upper() if self.sobrenome else ''
        return ini_nome + ini_sob

    def idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    def cpf_mascarado(self):
        c = self.cpf
        if len(c) == 11:
            return f'***.{c[3:6]}.{c[6:9]}-**'
        return c
