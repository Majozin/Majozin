"""Publica somente nomes e métricas agregadas em cartões locais."""
from pathlib import Path
import hashlib
from profile_theme import card, text, row, img, CYAN, PINK, MUTED, SURFACE


def render_projects(records):
    output=Path('assets/projects')
    output.mkdir(parents=True,exist_ok=True)
    cards=[]
    unmeasured=[]
    used=set()
    for item in records:
        name,percent,status=item['name'],item['percent'],item['status']
        if percent is None:
            unmeasured.append(name)
            continue
        if not 0 <= percent <= 100:
            raise ValueError('Percentual fora do intervalo')
        filename='progress-'+hashlib.sha256(name.encode()).hexdigest()[:16]+'.svg'
        used.add(filename)
        size=min(15,350/max(len(name),1))
        body=text('PROJETO PRIVADO',125,25,9,CYAN,mono=True,spacing=1)
        body+=text(name,125,51,size,weight='700')
        body+=text(str(percent)+'%',125,84,29,CYAN,weight='700',mono=True)
        body+=text(status,125,105,11,MUTED)
        body+=f'<rect x="18" y="122" width="214" height="7" fill="{SURFACE}"/><rect x="18" y="122" width="{214*percent/100:g}" height="7" fill="{CYAN}"/>'
        (output/filename).write_text(card(name+': '+str(percent)+'% — '+status,body,height=150),encoding='utf-8')
        cards.append(img('assets/projects/'+filename,name+': '+str(percent)+'% — '+status))
    lines=[row(cards[i:i+3]) for i in range(0,len(cards),3)]
    if unmeasured:
        lines+=['<h4 align="center">Outros projetos · sem estimativa</h4>']
        catalog=[]
        for i in range(0,len(unmeasured),4):
            group=unmeasured[i:i+4]
            filename=f'catalog-{i//4+1}.svg'
            used.add(filename)
            body=text('EM MEU LABORATÓRIO',125,28,9,PINK,mono=True,spacing=0.8)
            body+='<path d="M22 41h206" stroke="#2A3D56"/>'
            for j,name in enumerate(group):
                body+=text(name,125,67+j*27,min(13,350/max(len(name),1)))
            (output/filename).write_text(card('Projetos sem estimativa: '+', '.join(group),body,height=170,accent=PINK),encoding='utf-8')
            catalog.append(img('assets/projects/'+filename,'Sem estimativa: '+', '.join(group)))
        lines += [row(catalog[i:i+3]) for i in range(0,len(catalog),3)]
    for pattern in ('progress-*.svg','catalog-*.svg'):
        for old in output.glob(pattern):
            if old.name not in used:
                old.unlink()
    return '\n\n'.join(lines)
