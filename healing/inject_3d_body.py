import os
import re

files = [
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\form_atendimento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\detalhar_atendimento.html'
]

css_body_map = """
/* ── 3D Anatomic Body Map CSS ──────────────────────── */
.bodymap-svg-panel {
  background: #000; /* Dark background to match the 3D render */
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
  border-right: 1px solid rgba(255,255,255,0.05);
}

#bodySvg {
  width: 280px;
  max-width: 100%;
  height: auto;
  display: block;
  user-select: none;
}

.pulse-dot {
  fill: rgba(255, 255, 255, 0.6);
  stroke: rgba(255, 255, 255, 0.9);
  stroke-width: 2;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: center;
}

.pulse-dot:hover {
  fill: #f59e0b; /* Amber */
  stroke: rgba(245, 158, 11, 0.5);
  stroke-width: 15;
}

.pulse-dot.selected {
  fill: #ef4444; /* Red / Danger */
  stroke: rgba(239, 68, 68, 0.4);
  stroke-width: 25;
  animation: pulseBeat3D 2s infinite alternate;
}

@keyframes pulseBeat3D {
  0% { stroke-width: 15; filter: drop-shadow(0 0 10px rgba(239,68,68,0.6)); }
  100% { stroke-width: 30; filter: drop-shadow(0 0 20px rgba(239,68,68,1)); }
}

/* Glass Scan Line */
.glass-scan {
  fill: url(#scanGradient);
  opacity: 0.9;
  animation: scanMove 4s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}

@keyframes scanMove {
  0% { transform: translateY(-50px); }
  100% { transform: translateY(1050px); }
}

.bodymap-svg-label {
  font-family: var(--font-display);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin-bottom: 10px;
  z-index: 10;
}
"""

svg_body_map = """
      <!-- ═══ 3D ANATOMIC BODY SVG ═════════════════════════════════ -->
      <svg id="bodySvg" viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="scanGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#0ea5e9" stop-opacity="0" />
            <stop offset="50%" stop-color="#0ea5e9" stop-opacity="0.6" />
            <stop offset="100%" stop-color="#0ea5e9" stop-opacity="0" />
          </linearGradient>
        </defs>

        <!-- ── 3D Render Image Background ──────────────── -->
        <image href="{% static 'img/body_3d.png' %}" x="0" y="0" width="1000" height="1000" preserveAspectRatio="xMidYMid slice" />

        <!-- ── GLASS SCAN LINE ─────────────────────────────── -->
        <rect class="glass-scan" x="0" y="0" width="1000" height="80" rx="40"/>

        <!-- ── PULSE DOTS (CLICKABLE ZONES) ──────────────────────── -->
        <circle id="bz-cabeca"       class="pulse-dot bz" data-label="Cabeça"       cx="500" cy="150" r="12"/>
        <circle id="bz-pescoco"      class="pulse-dot bz" data-label="Pescoço"      cx="500" cy="240" r="12"/>
        <circle id="bz-ombro_esq"   class="pulse-dot bz" data-label="Ombro Esq."   cx="380" cy="280" r="12"/>
        <circle id="bz-ombro_dir"   class="pulse-dot bz" data-label="Ombro Dir."   cx="620" cy="280" r="12"/>
        <circle id="bz-torax_esq"   class="pulse-dot bz" data-label="Tórax Esq."   cx="430" cy="380" r="12"/>
        <circle id="bz-torax_dir"   class="pulse-dot bz" data-label="Tórax Dir."   cx="570" cy="380" r="12"/>
        <circle id="bz-abdomen_sup" class="pulse-dot bz" data-label="Abdômen Sup." cx="500" cy="460" r="12"/>
        <circle id="bz-abdomen_inf" class="pulse-dot bz" data-label="Abdômen Inf." cx="500" cy="550" r="12"/>
        <circle id="bz-braco_esq"   class="pulse-dot bz" data-label="Braço Esq."   cx="330" cy="420" r="12"/>
        <circle id="bz-braco_dir"   class="pulse-dot bz" data-label="Braço Dir."   cx="670" cy="420" r="12"/>
        <circle id="bz-antebraco_esq" class="pulse-dot bz" data-label="Antebraço Esq." cx="280" cy="550" r="12"/>
        <circle id="bz-antebraco_dir" class="pulse-dot bz" data-label="Antebraço Dir." cx="720" cy="550" r="12"/>
        <circle id="bz-quadril_esq" class="pulse-dot bz" data-label="Quadril Esq." cx="440" cy="590" r="12"/>
        <circle id="bz-quadril_dir" class="pulse-dot bz" data-label="Quadril Dir." cx="560" cy="590" r="12"/>
        <circle id="bz-coxa_esq"    class="pulse-dot bz" data-label="Coxa Esq."    cx="420" cy="700" r="12"/>
        <circle id="bz-coxa_dir"    class="pulse-dot bz" data-label="Coxa Dir."    cx="580" cy="700" r="12"/>
        <circle id="bz-joelho_esq"  class="pulse-dot bz" data-label="Joelho Esq."  cx="420" cy="800" r="12"/>
        <circle id="bz-joelho_dir"  class="pulse-dot bz" data-label="Joelho Dir."  cx="580" cy="800" r="12"/>
        <circle id="bz-perna_esq"   class="pulse-dot bz" data-label="Perna Esq."   cx="420" cy="900" r="12"/>
        <circle id="bz-perna_dir"   class="pulse-dot bz" data-label="Perna Dir."   cx="580" cy="900" r="12"/>

      </svg>
      <!-- /bodySvg -->
"""

def update_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace CSS block
    content = re.sub(r'/\* ── Premium High-End Body Map CSS.*?</style>', css_body_map + '\n</style>', content, flags=re.DOTALL)
    
    # In case the previous script failed or the marker is missing:
    if '/* ── Premium High-End Body Map CSS' not in content:
         content = re.sub(r'\.bodymap-svg-panel \{.*?(?=\n\.bodymap-info-panel|\n</style>)', css_body_map, content, flags=re.DOTALL)

    # Replace SVG block
    content = re.sub(r'<svg id="bodySvg".*?</svg>', svg_body_map, content, flags=re.DOTALL)

    if 'detalhar_atendimento.html' in filepath:
        content = content.replace('cursor: pointer;', 'pointer-events: none;')
        content = content.replace('.pulse-dot:hover', '.pulse-dot-no-hover')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for f in files:
    update_file(f)
