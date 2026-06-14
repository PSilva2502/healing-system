import os

files = [
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\listar_consultas.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\detalhar_atendimento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\form_agendamento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\form_atendimento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\pacientes\templates\pacientes\listar_pacientes.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\pacientes\templates\pacientes\detalhar_paciente.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\pacientes\templates\pacientes\form_paciente.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\medicos\templates\medicos\listar_medicos.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\medicos\templates\medicos\form_medico.html',
]

replacements = {
    'class="glass-card"': 'class="bento-card reveal"',
    'class="glass-card ': 'class="bento-card reveal ',
    'class="page-header"': 'class="futuristic-header reveal d-1"',
    'class="page-title"': 'class="f-title"',
    'class="page-subtitle"': 'class="f-subtitle"',
    'class="wf-agenda"': 'class="wf-agenda bento-card reveal d-1" style="padding: 0;"',
    'class="wf-card\n': 'class="wf-card reveal d-2\n',
    'class="data-table"': 'class="data-table reveal d-2"',
}

for fp in files:
    if not os.path.exists(fp): continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
