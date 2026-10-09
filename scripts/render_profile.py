"""Gera os elementos estáticos do perfil usando a identidade compartilhada."""
from pathlib import Path
from profile_theme import card,text,CYAN,PINK,MUTED,BORDER


def main():
    output=Path('assets/profile')
    output.mkdir(parents=True,exist_ok=True)
    body='<defs><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="#23324A" stroke-width="0.6"/></pattern></defs>'
    body+='<rect x="24" y="24" width="732" height="142" fill="url(#grid)" opacity="0.55"/>'
    body+='<path d="M22 110h85l25-25h54M758 110h-85l-25-25h-54" fill="none" stroke="#2A3D56"/>'
    body+=text('CONSTRUIR / CONECTAR / APRIMORAR',390,38,10,CYAN,mono=True,spacing=2)
    body+=text('MAJOZIN',393,108,60,PINK,weight='700',mono=True,spacing=7)
    body+=text('MAJOZIN',390,105,60,weight='700',mono=True,spacing=7)
    body+=text('DESENVOLVIMENTO · AUTOMAÇÃO · INFRAESTRUTURA',390,146,12,MUTED,mono=True)
    Path('assets/header.svg').write_text(card('Majozin — Desenvolvimento, automação e infraestrutura',body,780,190),encoding='utf-8')
    body=text('MEU LABORATÓRIO',260,28,10,CYAN,mono=True,spacing=2)
    body+=text('Ideias que saem do papel.',260,59,23,weight='700')
    for i,line in enumerate(['Aqui reúno projetos que nascem de necessidades reais','e da vontade de experimentar. Entre sistemas de gestão,','integrações e infraestrutura self-hosted,','aprendo construindo e aprimoro usando.']):
        body+=text(line,260,91+21*i,13,MUTED)
    (output/'about.svg').write_text(card('Meu laboratório de ideias que saem do papel. Aqui reúno projetos que nascem de necessidades reais e da vontade de experimentar. Entre sistemas de gestão, integrações e infraestrutura self-hosted, aprendo construindo e aprimoro usando.',body,520,181),encoding='utf-8')
    groups=[('development','DESENVOLVIMENTO','Sistemas & dados',['Python · JavaScript','React · PostgreSQL'],CYAN),('infrastructure','INFRAESTRUTURA','Automação & operação',['Docker · Linux · Git','GitHub Actions · Cloudflare'],CYAN),('design','DESIGN','Interfaces & experiência',['Figma · Penpot','Prototipação · UX'],PINK)]
    for filename,label,title,items,accent in groups:
        body=text(label,125,29,9,accent,mono=True,spacing=1)
        body+=text(title,125,60,14,weight='700')
        body+='<path d="M24 76h202" stroke="#2A3D56"/>'
        for j,line in enumerate(items):body+=text(line,125,104+j*24,12,MUTED)
        (output/(filename+'.svg')).write_text(card(title+': '+', '.join(items),body,accent=accent),encoding='utf-8')
    body=text('PLANEJAR COM CLAREZA',390,28,11,CYAN,mono=True,spacing=1)
    body+=text('Construir com propósito. Aprimorar sempre.',390,53,14,MUTED)
    (output/'footer.svg').write_text(card('Planejar com clareza. Construir com propósito. Aprimorar sempre.',body,780,78,accent=PINK),encoding='utf-8')

if __name__=='__main__':main()
