import os
import re

files = [
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\form_atendimento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\detalhar_atendimento.html'
]

css_body_map = """
/* ── Premium High-End Body Map CSS ──────────────────────── */
.bodymap-svg-panel {
  background: transparent;
  padding: 30px 12px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: visible;
}

#bodySvg {
  width: 190px;
  height: auto;
  display: block;
  user-select: none;
  filter: drop-shadow(0 20px 40px rgba(0,0,0,0.1));
}

.body-stroke-gradient {
  fill: none;
  stroke: url(#bodyGradient);
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: all var(--t-smooth);
}

.pulse-dot {
  fill: rgba(255, 255, 255, 0.4);
  stroke: rgba(255, 255, 255, 0.8);
  stroke-width: 1.5;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: center;
}

.pulse-dot:hover {
  fill: #f59e0b; /* Amber */
  stroke: rgba(245, 158, 11, 0.4);
  stroke-width: 8;
  transform: scale(1.3);
}

.pulse-dot.selected {
  fill: #ef4444; /* Red / Danger */
  stroke: rgba(239, 68, 68, 0.3);
  stroke-width: 12;
  animation: pulseBeat 2s infinite alternate;
}

@keyframes pulseBeat {
  0% { stroke-width: 8; filter: drop-shadow(0 0 4px rgba(239,68,68,0.5)); }
  100% { stroke-width: 14; filter: drop-shadow(0 0 12px rgba(239,68,68,0.8)); }
}

/* Glass Scan Line */
.glass-scan {
  fill: url(#scanGradient);
  opacity: 0.8;
  animation: scanMove 4s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}

@keyframes scanMove {
  0% { transform: translateY(-20px); }
  100% { transform: translateY(480px); }
}

/* Label overlay */
.bodymap-svg-label {
  font-family: var(--font-display);
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 24px;
}
"""

svg_body_map = """
      <!-- ═══ PREMIUM BODY SVG ═════════════════════════════════ -->
      <svg id="bodySvg" viewBox="0 0 200 490" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bodyGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--text-secondary)" stop-opacity="0.9" />
            <stop offset="100%" stop-color="var(--text-muted)" stop-opacity="0.3" />
          </linearGradient>
          <linearGradient id="scanGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--accent)" stop-opacity="0" />
            <stop offset="50%" stop-color="var(--accent)" stop-opacity="0.4" />
            <stop offset="100%" stop-color="var(--accent)" stop-opacity="0" />
          </linearGradient>
        </defs>

        <!-- ── VOLUMETRIC BODY OUTLINE ──────────────── -->
        <g class="body-stroke-gradient">
          <ellipse cx="100" cy="46" rx="30" ry="36"/>
          <path d="M88 80 L88 106 L112 106 L112 80"/>
          <path d="M46 106 Q40 130 36 160 L34 248 Q36 262 52 268 L100 274 L148 268 Q164 262 166 248 L164 160 Q160 130 154 106"/>
          <path d="M46 106 L30 148 L22 196 L18 238"/>
          <ellipse cx="15" cy="247" rx="9" ry="14"/>
          <path d="M154 106 L170 148 L178 196 L182 238"/>
          <ellipse cx="185" cy="247" rx="9" ry="14"/>
          <path d="M52 268 Q46 286 48 308 L72 316 L128 316 L152 308 Q154 286 148 268"/>
          <path d="M72 316 L64 392 L60 454"/>
          <ellipse cx="57" cy="462" rx="18" ry="9"/>
          <path d="M128 316 L136 392 L140 454"/>
          <ellipse cx="143" cy="462" rx="18" ry="9"/>
        </g>

        <!-- Spine/Sternum Details (Ultra Subtle) -->
        <line x1="100" y1="106" x2="100" y2="274" stroke="var(--text-muted)" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.3"/>
        <path d="M66 126 Q100 130 134 126" fill="none" stroke="var(--text-muted)" stroke-width="0.5" opacity="0.2"/>
        <path d="M60 140 Q100 144 140 140" fill="none" stroke="var(--text-muted)" stroke-width="0.5" opacity="0.2"/>
        <path d="M56 154 Q100 158 144 154" fill="none" stroke="var(--text-muted)" stroke-width="0.5" opacity="0.2"/>

        <!-- ── GLASS SCAN LINE ─────────────────────────────── -->
        <rect class="glass-scan" x="-20" y="0" width="240" height="40" rx="20"/>

        <!-- ── PULSE DOTS (CLICKABLE ZONES) ──────────────────────── -->
        <circle id="bz-cabeca"       class="pulse-dot bz" data-label="Cabeça"       cx="100" cy="46" r="6"/>
        <circle id="bz-pescoco"      class="pulse-dot bz" data-label="Pescoço"      cx="100" cy="93" r="6"/>
        <circle id="bz-ombro_esq"   class="pulse-dot bz" data-label="Ombro Esq."   cx="44"  cy="108" r="6"/>
        <circle id="bz-ombro_dir"   class="pulse-dot bz" data-label="Ombro Dir."   cx="156" cy="108" r="6"/>
        <circle id="bz-torax_esq"   class="pulse-dot bz" data-label="Tórax Esq."   cx="73"  cy="137" r="6"/>
        <circle id="bz-torax_dir"   class="pulse-dot bz" data-label="Tórax Dir."   cx="127" cy="137" r="6"/>
        <circle id="bz-abdomen_sup" class="pulse-dot bz" data-label="Abdômen Sup." cx="100" cy="193" r="6"/>
        <circle id="bz-abdomen_inf" class="pulse-dot bz" data-label="Abdômen Inf." cx="100" cy="244" r="6"/>
        <circle id="bz-braco_esq"   class="pulse-dot bz" data-label="Braço Esq."   cx="32"  cy="146" r="6"/>
        <circle id="bz-braco_dir"   class="pulse-dot bz" data-label="Braço Dir."   cx="168" cy="146" r="6"/>
        <circle id="bz-antebraco_esq" class="pulse-dot bz" data-label="Antebraço Esq." cx="24" cy="216" r="6"/>
        <circle id="bz-antebraco_dir" class="pulse-dot bz" data-label="Antebraço Dir." cx="176" cy="216" r="6"/>
        <circle id="bz-quadril_esq" class="pulse-dot bz" data-label="Quadril Esq." cx="72"  cy="293" r="6"/>
        <circle id="bz-quadril_dir" class="pulse-dot bz" data-label="Quadril Dir." cx="128" cy="293" r="6"/>
        <circle id="bz-coxa_esq"    class="pulse-dot bz" data-label="Coxa Esq."    cx="64"  cy="355" r="6"/>
        <circle id="bz-coxa_dir"    class="pulse-dot bz" data-label="Coxa Dir."    cx="136" cy="355" r="6"/>
        <circle id="bz-joelho_esq"  class="pulse-dot bz" data-label="Joelho Esq."  cx="64"  cy="397" r="6"/>
        <circle id="bz-joelho_dir"  class="pulse-dot bz" data-label="Joelho Dir."  cx="136" cy="397" r="6"/>
        <circle id="bz-perna_esq"   class="pulse-dot bz" data-label="Perna Esq."   cx="64"  cy="446" r="6"/>
        <circle id="bz-perna_dir"   class="pulse-dot bz" data-label="Perna Dir."   cx="136" cy="446" r="6"/>

      </svg>
      <!-- /bodySvg -->
"""

def update_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the style block for bodymap and replace it
    if '/* ── Body-map card' in content or '.bodymap-svg-panel {' in content:
        # We need to replace the specific css rules for .bodymap-svg-panel, #bodySvg, .bz, .scan-line
        # Since they might be scattered, we'll replace the block that starts with .bodymap-svg-panel to the end of style
        content = re.sub(r'\.bodymap-svg-panel \{.*?\}(?=\n\.bodymap-info-panel|\n</style>)', css_body_map, content, flags=re.DOTALL)
        content = re.sub(r'\.bz \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\.bz:hover \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\.bz\.selected \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'body\.dark \.bz\.selected \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\#bodySvg \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\.scan-line \{.*?\}', '', content, flags=re.DOTALL)
        content = re.sub(r'@keyframes bodyScan \{.*?\}', '', content, flags=re.DOTALL)
        
        # Inject our new CSS before </style> just in case
        content = content.replace('</style>', css_body_map + '\n</style>')

    # Replace SVG completely
    content = re.sub(r'<svg id="bodySvg".*?</svg>', svg_body_map, content, flags=re.DOTALL)

    # In detalhar_atendimento, make pulse dots pointer-events none
    if 'detalhar_atendimento.html' in filepath:
        content = content.replace('cursor: pointer;', 'pointer-events: none;')
        content = content.replace('.pulse-dot:hover', '.pulse-dot-no-hover')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for f in files:
    update_file(f)
