"""
Script para popular o banco com dados de exemplo.
Execute: python popular_dados.py
"""
import os
import django
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Usuario
from pacientes.models import Paciente
from medicos.models import Medico
from consultas.models import Consulta


def criar_dados():
    print("Criando usuários de exemplo...")

    # Admin
    admin, _ = Usuario.objects.get_or_create(
        email='admin@healing.com',
        defaults={
            'username': 'admin@healing.com',
            'first_name': 'Carlos',
            'last_name': 'Administrador',
            'perfil': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin.set_password('admin123')
    admin.save()
    print(f"  Admin:          admin@healing.com / admin123")

    # Recepcionista
    recepc, _ = Usuario.objects.get_or_create(
        email='recepcao@healing.com',
        defaults={
            'username': 'recepcao@healing.com',
            'first_name': 'Mariana',
            'last_name': 'Recepção',
            'perfil': 'recepcionista',
        }
    )
    recepc.set_password('recepcao123')
    recepc.save()
    print(f"  Recepcionista:  recepcao@healing.com / recepcao123")

    # Médicos
    dados_medicos = [
        ('Ana', 'Carvalho', 'ana@healing.com', 'CRM/BA 12345', 'Cardiologia'),
        ('Roberto', 'Silva', 'roberto@healing.com', 'CRM/BA 67890', 'Neurologia'),
        ('Fernanda', 'Costa', 'fernanda@healing.com', 'CRM/BA 11111', 'Pediatria'),
    ]

    medicos_criados = []
    for nome, sobrenome, email, crm, especialidade in dados_medicos:
        usuario_med, _ = Usuario.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': nome,
                'last_name': sobrenome,
                'perfil': 'medico',
            }
        )
        usuario_med.set_password('medico123')
        usuario_med.save()

        medico, _ = Medico.objects.get_or_create(
            usuario=usuario_med,
            defaults={'crm': crm, 'especialidade': especialidade}
        )
        medicos_criados.append(medico)
        print(f"  Médico:         {email} / medico123")

    # Pacientes (sem conta de usuário — gerenciados pela recepção)
    dados_pacientes = [
        ('João', 'Santos', 'joao@email.com', '12345678901', '71999000001', date(1985, 3, 15)),
        ('Maria', 'Oliveira', 'maria@email.com', '98765432100', '71999000002', date(1992, 7, 22)),
        ('Pedro', 'Lima', 'pedro@email.com', '45612378934', '71999000003', date(2001, 11, 5)),
    ]

    pacientes_criados = []
    for nome, sobrenome, email, cpf, tel, nasc in dados_pacientes:
        paciente, _ = Paciente.objects.get_or_create(
            cpf=cpf,
            defaults={
                'nome': nome,
                'sobrenome': sobrenome,
                'email': email,
                'telefone': tel,
                'data_nascimento': nasc,
            }
        )
        pacientes_criados.append(paciente)
        print(f"  Paciente:       {nome} {sobrenome}")

    # Consultas
    hoje = date.today()
    consultas = [
        (pacientes_criados[0], medicos_criados[0], hoje, time(9, 0), 'agendada', 'Checkup cardíaco'),
        (pacientes_criados[1], medicos_criados[1], hoje, time(10, 30), 'agendada', 'Dor de cabeça persistente'),
        (pacientes_criados[2], medicos_criados[2], hoje - timedelta(days=3), time(8, 0), 'realizada', ''),
        (pacientes_criados[0], medicos_criados[1], hoje + timedelta(days=5), time(14, 0), 'agendada', ''),
    ]

    for pac, med, data, hora, status, obs in consultas:
        Consulta.objects.get_or_create(
            paciente=pac,
            medico=med,
            data_consulta=data,
            horario=hora,
            defaults={'status': status, 'observacoes': obs}
        )

    print("\nDados criados com sucesso!")
    print("\n=== CREDENCIAIS DE ACESSO ===")
    print("Admin:          admin@healing.com       / admin123")
    print("Recepcionista:  recepcao@healing.com    / recepcao123")
    print("Médico:         ana@healing.com         / medico123")
    print("=============================")


if __name__ == '__main__':
    criar_dados()
