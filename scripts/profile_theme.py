"""Identidade cyberpunk compartilhada pelos SVGs do perfil."""
from html import escape

BG = '#090D18'
SURFACE = '#101828'
BORDER = '#2A3D56'
TEXT = '#EAF4FF'
MUTED = '#A9BCD3'
CYAN = '#59F3F2'
PINK = '#FC77C8'
MONO = 'DejaVu Sans Mono, monospace'
SANS = 'DejaVu Sans, Arial, sans-serif'


def text(value, x, y, size=13, fill=TEXT, weight='400', mono=False, spacing=None):
    tracking = f' letter-spacing="{spacing}"' if spacing is not None else ''
    return f'<text x="{x}" y="{y}" text-anchor="middle" fill="{fill}" font-family="{MONO if mono else SANS}" font-size="{size}" font-weight="{weight}"{tracking}>{escape(str(value))}</text>'


def card(title, body, width=250, height=170, accent=CYAN):
    w,h=width,height
    frame=f'M13 1H{w-25}L{w-1} 25V{h-13}L{w-13} {h-1}H25L1 {h-25}V13Z'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<path d="{frame}" fill="{BG}" stroke="{BORDER}"/>
<path d="M14 1H72M{w-1} {h-65}V{h-14}L{w-14} {h-1}H{w-55}" fill="none" stroke="{accent}" stroke-width="2"/>
<path d="M{w-42} 11h14m-10 5h14" stroke="{accent}" opacity="0.65"/>
{body}
</svg>'''


def row(images):
    return '<p align="center">\n'+'\n'.join(images)+'\n</p>'


def img(path, alt, width=250):
    return f'<img src="{escape(path, quote=True)}" width="{width}" alt="{escape(alt, quote=True)}" />'
