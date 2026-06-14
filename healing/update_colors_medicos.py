import os

files = [
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\medicos\templates\medicos\listar_medicos.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\medicos\templates\medicos\form_medico.html'
]

replacements = {
    'background:linear-gradient(135deg,#0891b2,#22d3ee);': 'background:var(--accent-soft);color:var(--accent-deep);border:1px solid var(--accent-border);',
    'color:#e2e8f0;': 'color:var(--text-primary);',
    'color:rgba(100,116,139,0.6);': 'color:var(--text-muted);',
    'color:rgba(148,163,184,0.7);': 'color:var(--text-secondary);',
    'color:#c4b5fd;': 'color:var(--info);',
    'color:rgba(100,116,139,0.5);': 'color:var(--text-faint);',
    'color:rgba(148,163,184,0.6);': 'color:var(--text-muted);',
    'border-top:1px solid rgba(255,255,255,0.06);': 'border-top:1px solid var(--border-l);',
    'border-bottom:1px solid rgba(255,255,255,0.04);': 'border-bottom:1px solid var(--border-l);',
    'class="btn-cyan"': 'class="btn-secondary"',
    "class='btn-cyan'": "class='btn-secondary'"
}

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
