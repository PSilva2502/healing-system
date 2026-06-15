from django.core.management.base import BaseCommand
from consultas.models import TipoConsulta, TabelaValor, TemplateEspecialidade
from pacientes.models import Convenio


TEMPLATES = [
    ('Cardiologia', ['Pressão Arterial', 'Frequência Cardíaca', 'Resultado ECG', 'Ausculta', 'Risco Cardiovascular']),
    ('Dermatologia', ['Tipo de Lesão', 'Região Afetada', 'Dermatoscopia']),
    ('Ortopedia', ['Articulação Afetada', 'Amplitude de Movimento', 'Resultado Raio-X']),
    ('Pediatria', ['Peso (kg)', 'Altura (cm)', 'Perímetro Cefálico', 'Vacinação em dia']),
    ('Clínica Geral', ['Pressão Arterial', 'Peso (kg)', 'Temperatura']),
]


CONVENIOS = [
    ('Unimed', 30),
    ('Bradesco Saúde', 25),
    ('SulAmérica', 20),
]

TIPOS = [
    ('Consulta de Rotina', 'Clínica Geral', 250, [
        'Pressão Arterial', 'Peso (kg)', 'Temperatura',
    ]),
    ('Avaliação Cardiológica', 'Cardiologia', 450, [
        'Pressão Arterial', 'Frequência Cardíaca', 'Resultado ECG',
        'Ausculta', 'Risco Cardiovascular',
    ]),
    ('Consulta Dermatológica', 'Dermatologia', 350, [
        'Tipo de Lesão', 'Região Afetada', 'Dermatoscopia',
    ]),
    ('Retorno', 'Clínica Geral', 120, []),
]


class Command(BaseCommand):
    help = 'Popula convênios e tipos de consulta com valores (idempotente).'

    def handle(self, *args, **options):
        for nome, desc in CONVENIOS:
            c, criado = Convenio.objects.get_or_create(
                nome=nome, defaults={'desconto_percentual': desc},
            )
            self.stdout.write(f'{"+" if criado else "·"} Convênio: {c}')

        for nome, esp, valor, campos in TIPOS:
            campos_extras = [{'label': l, 'tipo': 'text'} for l in campos]
            t, criado = TipoConsulta.objects.get_or_create(
                nome=nome,
                defaults={'especialidade': esp, 'campos_extras': campos_extras},
            )
            if not criado:
                t.especialidade = esp
                t.campos_extras = campos_extras
                t.save()
            TabelaValor.objects.update_or_create(
                tipo_consulta=t, defaults={'valor_base': valor},
            )
            self.stdout.write(f'{"+" if criado else "·"} Tipo: {t.nome} — R$ {valor} ({len(campos)} campos)')

        for esp, campos in TEMPLATES:
            campos_extras = [{'label': l, 'tipo': 'text'} for l in campos]
            tpl, criado = TemplateEspecialidade.objects.get_or_create(
                especialidade=esp, defaults={'campos_extras': campos_extras},
            )
            if not criado:
                tpl.campos_extras = campos_extras
                tpl.save()
            self.stdout.write(f'{"+" if criado else "·"} Template: {esp} ({len(campos)} campos)')

        self.stdout.write(self.style.SUCCESS('Seed clínico concluído.'))
