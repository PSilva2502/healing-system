from django.db import models
from core.models import Usuario

ESPECIALIDADES = [
    ('Cardiologia', 'Cardiologia'),
    ('Dermatologia', 'Dermatologia'),
    ('Endocrinologia', 'Endocrinologia'),
    ('Gastroenterologia', 'Gastroenterologia'),
    ('Geriatria', 'Geriatria'),
    ('Ginecologia', 'Ginecologia'),
    ('Neurologia', 'Neurologia'),
    ('Oftalmologia', 'Oftalmologia'),
    ('Oncologia', 'Oncologia'),
    ('Ortopedia', 'Ortopedia'),
    ('Otorrinolaringologia', 'Otorrinolaringologia'),
    ('Pediatria', 'Pediatria'),
    ('Psiquiatria', 'Psiquiatria'),
    ('Reumatologia', 'Reumatologia'),
    ('Urologia', 'Urologia'),
    ('Clínica Geral', 'Clínica Geral'),
]


class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='medico')
    crm = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=100, choices=ESPECIALIDADES)
    foto = models.ImageField(upload_to='medicos/', blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'medico'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['especialidade', 'usuario__first_name']

    def __str__(self):
        return f'Dr(a). {self.usuario.get_full_name()} — {self.especialidade}'
