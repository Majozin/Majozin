"""Renderização pública: somente nomes e indicadores agregados."""
from html import escape
from pathlib import Path
import hashlib


def render_projects(records):
    output = Path("assets/projects")
    output.mkdir(parents=True, exist_ok=True)
    lines = ['<p align="center">']
    card_count = 0
    unmeasured = []
    used = set()
    for item in records:
        name, percent, status = item["name"], item["percent"], item["status"]
        if percent is None:
            unmeasured.append(name)
            continue
        if not 0 <= percent <= 100:
            raise ValueError("Percentual fora do intervalo")
        filename = "progress-" + hashlib.sha256(name.encode()).hexdigest()[:16] + ".svg"
        used.add(filename)
        label = escape(name)
        caption = escape(status)
        font_size = min(16, 390 / max(len(name), 1))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="250" height="150" viewBox="0 0 250 150" role="img" aria-labelledby="title desc">
<title id="title">{label}: {percent}%</title><desc id="desc">{caption}</desc>
<rect x="1" y="1" width="248" height="148" rx="12" fill="#F2F7FC" stroke="#C9D9E9"/>

<text x="125" y="25" text-anchor="middle" fill="#526C82" font-family="Arial, sans-serif" font-size="9" letter-spacing="1.2">PROJETO PRIVADO</text>
<text x="125" y="52" text-anchor="middle" fill="#203C55" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="700">{label}</text>
<text x="125" y="102" text-anchor="middle" fill="#526C82" font-family="Arial, sans-serif" font-size="11">{caption}</text>
<text x="125" y="81" text-anchor="middle" fill="#315F87" font-family="Arial, sans-serif" font-size="22" font-weight="700">{percent}%</text>
<rect x="18" y="120" width="214" height="8" rx="4" fill="#DCE7F1"/>
<rect x="18" y="120" width="{214*percent/100:g}" height="8" rx="4" fill="#547FA5"/>
</svg>'''
        (output / filename).write_text(svg, encoding="utf-8")
        if card_count and card_count % 3 == 0:
            lines.append('</p>\n<p align="center">')
        card_count += 1
        lines.append(f'<img src="assets/projects/{filename}" width="250" alt="{label}: {percent}% — {caption}" />')
    lines.append('</p>')
    if unmeasured:
        lines += ['', '<h4 align="center">Outros projetos · sem estimativa</h4>', '', '<p align="center">' + ' · '.join('<code>' + escape(n) + '</code>' for n in unmeasured) + '</p>']
    for old in output.glob('progress-*.svg'):
        if old.name not in used:
            old.unlink()
    return "\n".join(lines)
