from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

lines = [
'tesis_srs/',
'├── app/',
'│   ├── __init__.py',
'│   ├── routes.py',
'│   ├── models.py',
'│   ├── agents/',
'│   │   ├── transcription_agent.py',
'│   │   ├── requirements_agent.py',
'│   │   ├── enrichment_agent.py',
'│   │   └── srs_agent.py',
'│   ├── orchestrator/',
'│   │   └── orchestrator.py',
'│   ├── mcp/',
'│   │   ├── client.py',
'│   │   └── servers/',
'│   │       ├── web_server.py',
'│   │       ├── database_server.py',
'│   │       └── srs_server.py',
'│   ├── rag/',
'│   │   ├── retriever.py',
'│   │   └── context_builder.py',
'│   ├── services/',
'│   ├── templates/',
'│   └── static/',
'│       └── css/',
'│           └── style.css',
'├── instance/',
'│   └── srs.db',
'├── uploads/',
'├── config.py',
'├── requirements.txt',
'└── run.py',
]
S=2
W,H=1380,1810
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
regular=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',35*S)
bold=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',35*S)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34*S)
note=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25*S)
d.rounded_rectangle((35*S,30*S,(W-35)*S,(H-30)*S),radius=20*S,fill='#F8FAFC',outline='#BAC6D2',width=2*S)
d.text((W*S/2,83*S),'Organización de directorios y archivos',font=title,fill='#243648',anchor='mm')
d.line((80*S,130*S,(W-80)*S,130*S),fill='#BAC6D2',width=2*S)
for i,line in enumerate(lines):
    is_dir=line.endswith('/')
    d.text((100*S,(165+i*47)*S),line,font=bold if is_dir else regular,fill='#24597A' if is_dir else '#273747')
d.text((W*S/2,1730*S),'Estructura simplificada de los componentes principales.',font=note,fill='#435569',anchor='mm')
out=Path(__file__).parent/'estructura_directorios_prototipo.png'
im.save(out,dpi=(300,300))
print(out.resolve())
