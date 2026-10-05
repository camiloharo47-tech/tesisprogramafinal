from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

S = 3
W, H = 1200, 1510
im = Image.new('RGB', (W*S, H*S), 'white')
d = ImageDraw.Draw(im)
ink = '#243648'
def text(x,y,lines,size=23,bold=False):
    f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size*S)
    for i,t in enumerate(lines.split('\n')):
        d.text((x*S,(y+i*(size+9))*S),t,font=f,fill=ink,anchor='mt')
def rect(x,y,w,h,fill='#EDF3FA',radius=14):
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),radius=radius*S,fill=fill,outline=ink,width=2*S)
def arrow(y1,y2,label=None):
    x=580
    d.line((x*S,y1*S,x*S,y2*S),fill=ink,width=2*S)
    d.polygon([(x*S,y2*S),((x-6)*S,(y2-11)*S),((x+6)*S,(y2-11)*S)],fill=ink)
    if label:
        text(790,(y1+y2)/2-11,label,19)
def stage(y,n,title,body,fill):
    rect(215,y,730,134,fill)
    text(580,y+17,f'Agente {n} · {title}',26,True)
    text(580,y+61,body,22)

rect(340,20,480,60,'#F2F4F6',30)
text(580,38,'Entrevista registrada con audio',23,True)
arrow(80,120)
rect(90,120,1020,1190,'#FFFFFF',20)
rect(270,145,620,90,'#E5EDF8')
text(580,157,'ORQUESTADOR',26,True)
text(580,195,'Valida la entrevista y coordina la secuencia',21)
arrow(235,295)
text(130,318,'POR',18,True)
text(130,346,'ENTRE-',18,True)
text(130,374,'VISTA',18,True)
stage(295,1,'Transcripción','Convertir el audio a texto con Whisper.\nGuardar la transcripción de la entrevista.','#EAF2FC')
arrow(429,485,'Transcripción')
stage(485,2,'Requisitos funcionales','Extraer y validar candidatos con reglas y un LLM.\nGuardar los RF y su evidencia de origen.','#EAF2FC')
arrow(619,705,'RF registrados')
d.line((110*S,670*S,1085*S,670*S),fill='#A9B5C1',width=S)
text(130,736,'POR',18,True)
text(130,764,'PRO-',18,True)
text(130,792,'YECTO',18,True)
stage(705,3,'Enriquecimiento académico','Consultar Crossref y sintetizar evidencia académica.\nGuardar un contexto común para el proyecto.','#EAF5EE')
arrow(839,925,'Contexto y fuentes')
stage(925,4,'Generación del SRS','Integrar los RF del proyecto y el contexto disponible.\nCompletar apartados orientativos y guardar el SRS.','#FFF3DF')
arrow(1059,1115)
rect(285,1115,590,68,'#F2F4F6',30)
text(580,1136,'Documento SRS disponible para consulta',23,True)
text(600,1220,'Las etapas comparten información mediante los datos almacenados.',20)
text(600,1253,'Los agentes 3 y 4 consideran los RF acumulados del proyecto.',20)
text(600,1340,'Ante un error no resuelto, se detienen las etapas posteriores.',21)
text(600,1375,'Los resultados ya guardados se conservan.',21)
text(600,1450,'RF: requisitos funcionales · SRS: especificación de requisitos de software',18)
out=Path(__file__).parent/'proceso_agentes_orquestador.png'
im.save(out,dpi=(300,300))
print(out.resolve())
