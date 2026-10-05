from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

lines = [
'tesis_srs/',
'├── app/',
'│   ├── __init__.py',
'│   ├── routes.py',
'│   ├── models.py',
'│   ├── services/',
'│   │   ├── academic_search_service.py',
'│   │   ├── document_service.py',
'│   │   ├── ollama_service.py',
'│   │   ├── srs_guidance_service.py',
'│   │   └── whisper_service.py',
'│   ├── templates/',
'│   │   ├── base.html',
'│   │   ├── index.html',
'│   │   ├── interview.html',
'│   │   ├── project.html',
'│   │   ├── project_context.html',
'│   │   ├── requirements.html',
'│   │   └── srs.html',
'│   └── static/',
'│       └── css/',
'│           └── style.css',
'├── instance/',
'│   └── srs.db',
'├── uploads/',
'├── .gitignore',
'├── ACADEMIC_RAG.md',
'├── config.py',
'├── requirements.txt',
'└── run.py',
]
S=2
W,H=1480,1750
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
regular=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',35*S)
bold=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',35*S)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34*S)
note=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24*S)
d.rounded_rectangle((35*S,30*S,(W-35)*S,(H-30)*S),radius=20*S,fill='#F8FAFC',outline='#BAC6D2',width=2*S)
d.text((W*S/2,83*S),'Servicios, interfaz y configuración',font=title,fill='#243648',anchor='mm')
d.line((80*S,130*S,(W-80)*S,130*S),fill='#BAC6D2',width=2*S)
for i,line in enumerate(lines):
    is_dir=line.endswith('/')
    d.text((100*S,(165+i*47)*S),line,font=bold if is_dir else regular,fill='#24597A' if is_dir else '#273747')
d.text((W*S/2,1640*S),'Vista de los servicios de apoyo, la presentación y los archivos generales.',font=note,fill='#435569',anchor='mm')
d.text((W*S/2,1680*S),'El contenido de los audios y los archivos auxiliares se omite.',font=note,fill='#435569',anchor='mm')
out=Path(__file__).parent/'estructura_servicios_interfaz_configuracion.png'
im.save(out,dpi=(300,300))
print(out.resolve())
