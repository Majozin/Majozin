"""Renderização pública: somente nomes e indicadores agregados."""
from html import escape
from pathlib import Path
import hashlib


def render_projects(records):
    output = Path("assets/projects")
    output.mkdir(parents=True, exist_ok=True)
    lines = ['<p align="left">']
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
        font_size = min(21, 560 / max(len(name), 1))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="176" viewBox="0 0 390 176" role="img" aria-labelledby="title desc">
<title id="title">{label}: {percent}%</title><desc id="desc">{caption}</desc>
<rect x="1" y="1" width="388" height="174" rx="16" fill="#F2F7FC" stroke="#C9D9E9"/>
<path d="M25 28h18m-18 5h10" stroke="#547FA5" stroke-width="3" stroke-linecap="round"/>
<text x="52" y="34" fill="#526C82" font-family="Arial, sans-serif" font-size="11" letter-spacing="1.6">PROJETO PRIVADO</text>
<text x="25" y="69" fill="#203C55" font-family="Arial, sans-serif" font-size="{font_size}" font-weight="700">{label}</text>
<text x="25" y="103" fill="#526C82" font-family="Arial, sans-serif" font-size="13">{caption}</text>
<text x="365" y="104" text-anchor="end" fill="#315F87" font-family="Arial, sans-serif" font-size="23" font-weight="700">{percent}%</text>
<rect x="25" y="128" width="340" height="8" rx="4" fill="#DCE7F1"/>
<rect x="25" y="128" width="{340*percent/100:g}" height="8" rx="4" fill="#547FA5"/>
</svg>'''
        (output / filename).write_text(svg, encoding="utf-8")
        lines.append(f'<img src="assets/projects/{filename}" width="390" alt="{label}: {percent}% — {caption}" />')
    lines.append('</p>')
    if unmeasured:
        lines += ['', '#### Outros projetos · sem estimativa', '', ' · '.join('<code>' + escape(n) + '</code>' for n in unmeasured)]
    for old in output.glob('progress-*.svg'):
        if old.name not in used:
            old.unlink()
    return "\n".join(lines)
