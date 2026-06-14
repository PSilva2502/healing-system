import re

files = [
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\form_atendimento.html',
    r'c:\Users\pedro\Documents\Healing\healing-system\healing\consultas\templates\consultas\detalhar_atendimento.html'
]

css_panel_new = """
.bodymap-svg-panel {
  background: var(--surface-solid);
  background-image: 
    linear-gradient(rgba(14, 165, 233, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14, 165, 233, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: center;
  border-right: 1px solid var(--border);
  box-shadow: inset 0 0 40px rgba(0,0,0,0.4);
  padding: 16px 12px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
"""

css_svg_new = """
#bodySvg {
  width: 176px;
  height: auto;
  display: block;
  user-select: none;
  filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.6));
}
"""

css_zones_new = """
.bz {
  fill: transparent;
  cursor: pointer;
  transition: fill 0.18s ease, filter 0.18s ease;
}
.bz:hover {
  fill: rgba(14, 165, 233, 0.2);
  filter: drop-shadow(0 0 5px rgba(14, 165, 233, 0.5));
}
.bz.selected {
  fill: rgba(14, 165, 233, 0.4);
  filter: drop-shadow(0 0 10px rgba(14, 165, 233, 0.9));
}
"""

css_zones_detalhar_new = """
.bz {
  fill: transparent;
  transition: fill 0.18s ease;
  pointer-events: none;
}
.bz.selected {
  fill: rgba(14, 165, 233, 0.4);
  filter: drop-shadow(0 0 10px rgba(14, 165, 233, 0.9));
}
body.dark .bz.selected {
  fill: rgba(14, 165, 233, 0.5);
  filter: drop-shadow(0 0 10px rgba(14, 165, 233, 1));
}
"""

pill_css_new = """
.zone-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px 4px 8px;
  border-radius: 20px;
  font-size: 0.70rem;
  font-weight: 600;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid var(--accent);
  animation: pillIn 0.20s var(--ease-bounce) both;
}

.zone-pill-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  animation: pulseDot 1.8s ease-in-out infinite;
  box-shadow: 0 0 5px var(--accent);
}
"""

def process_file(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace .bodymap-svg-panel block completely
    content = re.sub(r'\.bodymap-svg-panel \{.*?\}(?=\n\n|\n\.body|\nbody)', css_panel_new.strip(), content, flags=re.DOTALL)
    
    # Replace #bodySvg block
    content = re.sub(r'\#bodySvg \{.*?\}', css_svg_new.strip(), content, flags=re.DOTALL)

    # Replace .bz / .bz:hover / .bz.selected blocks in form_atendimento
    if 'form_atendimento' in fp:
        content = re.sub(r'\.bz \{.*?\.bz\.selected \{.*?\}', css_zones_new.strip(), content, flags=re.DOTALL)
        content = re.sub(r'\.zone-pill \{.*?\.zone-pill-dot \{.*?\}', pill_css_new.strip(), content, flags=re.DOTALL)
        # Update scan line to glowing cyan
        content = content.replace('fill="rgba(76,118,143,0.30)"', 'fill="rgba(14,165,233,0.8)" filter="drop-shadow(0 0 5px rgba(14,165,233,1))"')
    else:
        content = re.sub(r'\.bz \{.*?body\.dark \.bz\.selected \{.*?\}', css_zones_detalhar_new.strip(), content, flags=re.DOTALL)
        # Remove old stroke color blocks
        content = re.sub(r'/\* Body SVG stroke colors adapt to theme \*/.*?\}', '', content, flags=re.DOTALL)

    # Remove background <rect fill="#050818"> inside the SVG (if present)
    content = re.sub(r'<rect width="200" height="490" fill="#050818" rx="10"/>', '', content)
    content = re.sub(r'<rect width="200" height="490" fill="transparent" rx="10"/>', '', content)

    # Change all sage stroke colors to cyan
    content = content.replace('stroke="rgba(101,132,115,0.05)"', 'stroke="rgba(14,165,233,0.10)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.06)"', 'stroke="rgba(14, 165, 233, 0.10)"')
    content = content.replace('stroke="rgba(101,132,115,0.06)"', 'stroke="rgba(14,165,233,0.10)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.07)"', 'stroke="rgba(14, 165, 233, 0.12)"')
    content = content.replace('stroke="rgba(101,132,115,0.07)"', 'stroke="rgba(14,165,233,0.12)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.08)"', 'stroke="rgba(14, 165, 233, 0.15)"')
    content = content.replace('stroke="rgba(101,132,115,0.10)"', 'stroke="rgba(14,165,233,0.20)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.10)"', 'stroke="rgba(14, 165, 233, 0.20)"')
    content = content.replace('stroke="rgba(101,132,115,0.12)"', 'stroke="rgba(14,165,233,0.30)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.14)"', 'stroke="rgba(14, 165, 233, 0.30)"')
    content = content.replace('stroke="rgba(101,132,115,0.16)"', 'stroke="rgba(14,165,233,0.40)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.16)"', 'stroke="rgba(14, 165, 233, 0.40)"')
    content = content.replace('stroke="rgba(101,132,115,0.18)"', 'stroke="rgba(14,165,233,0.50)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.18)"', 'stroke="rgba(14, 165, 233, 0.50)"')
    content = content.replace('stroke="rgba(101,132,115,0.20)"', 'stroke="rgba(14,165,233,0.60)"')
    content = content.replace('stroke="rgba(101, 132, 115, 0.20)"', 'stroke="rgba(14, 165, 233, 0.60)"')

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)

for fp in files:
    process_file(fp)
