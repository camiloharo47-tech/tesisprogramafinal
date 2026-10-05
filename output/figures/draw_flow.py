from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

S=2
W,H=1600,2240
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
regular='C:/Windows/Fonts/arial.ttf'
bold='C:/Windows/Fonts/arialbd.ttf'
ink='#23364A'; blue='#E9F2FC'; green='#EAF6EF'; amber='#FFF3D9'; grey='#F1F3F5'

def font(size=28,b=False): return ImageFont.truetype(bold if b else regular,size*S)
def text(x,y,lines,size=28,b=False,color=ink):
    if isinstance(lines,str): lines=lines.split('\n')
    f=font(size,b); step=(size+10)*S
    total=len(lines)*step
    for i,line in enumerate(lines):
        box=d.textbbox((0,0),line,font=f)
        d.text((x*S-(box[2]-box[0])/2,y*S-total/2+i*step),line,font=f,fill=color)
def line(points,arrow=True):
    pts=[(int(x*S),int(y*S)) for x,y in points]
    d.line(pts,fill=ink,width=3*S,joint='curve')
    if arrow:
        x,y=pts[-1]; px,py=pts[-2]; a=math.atan2(y-py,x-px)
        size=12*S
        tri=[(x,y),(x-size*math.cos(a-.43),y-size*math.sin(a-.43)),(x-size*math.cos(a+.43),y-size*math.sin(a+.43))]
        d.polygon(tri,fill=ink)
def box(x,y,w,h,label,fill=blue,size=28,terminal=False):
    d.rounded_rectangle(((x-w/2)*S,(y-h/2)*S,(x+w/2)*S,(y+h/2)*S),radius=(h/2 if terminal else 12)*S,fill=fill,outline=ink,width=2*S)
    text(x,y,label,size,terminal)
def decision(y,label):
    x=800; w=460; h=136
    d.polygon([(x*S,(y-h/2)*S),((x+w/2)*S,y*S),(x*S,(y+h/2)*S),((x-w/2)*S,y*S)],fill=amber,outline=ink,width=2*S)
    text(x,y,label,27)
def label(x,y,t): text(x,y,t,24,True)

box(800,55,240,66,'Inicio',green,terminal=True)
line([(800,88),(800,130)])
box(800,177,740,94,'Seleccionar proyecto y cargar audio')
line([(800,224),(800,262)])
decision(330,'¿Archivo válido?')
line([(570,330),(320,330)])
label(445,309,'No')
box(170,330,300,104,'Solicitar otro\narchivo',grey,26)
line([(170,278),(170,177),(430,177)])
line([(800,398),(800,443)])
label(830,421,'Sí')
box(800,487,740,88,'Guardar audio y registrar entrevista')
line([(800,531),(800,571)])
box(800,620,740,98,'Agente 1 · Transcribir con Whisper\ny almacenar la transcripción')
line([(800,669),(800,709)])
box(800,768,740,118,'Agente 2 · Extraer y analizar RF\nGuardar requisitos y evidencia de entrevista')
line([(800,827),(800,872)])
decision(940,'¿El proyecto\ntiene RF?')
line([(570,940),(320,940)])
label(445,918,'No')
box(170,940,300,112,'Informar ausencia\nde requisitos',grey,26)
line([(170,996),(170,1040)])
box(170,1080,290,80,'Fin sin SRS',green,26,True)
line([(800,1008),(800,1053)])
label(830,1030,'Sí')
box(800,1112,740,118,'Agente 3 · Consultar artículos en Crossref\nmediante MCP, para el proyecto')
line([(800,1171),(800,1216)])
decision(1284,'¿Hay resúmenes\nrelevantes?')
line([(800,1352),(800,1400)])
label(830,1375,'Sí')
box(800,1460,740,120,'Generar síntesis con evidencia\ny guardar el contexto del proyecto')
line([(1030,1284),(1410,1284),(1410,1395)])
label(1170,1261,'No')
box(1410,1460,320,130,'Registrar ausencia\nde evidencia\nsin generar síntesis',grey,25)
line([(800,1520),(800,1590)],False)
line([(1410,1525),(1410,1565),(800,1565)],False)
d.ellipse((794*S,1559*S,806*S,1571*S),fill=ink)
line([(800,1565),(800,1608)])
box(800,1670,740,124,'Agente 4 · Construir el SRS\nRF originales, contexto académico\ny secciones orientativas',size=27)
line([(800,1732),(800,1772)])
box(800,1816,740,88,'Almacenar el documento SRS')
line([(800,1860),(800,1900)])
box(800,1952,740,104,'Mostrar el SRS y permitir\nsu descarga en Word')
line([(800,2004),(800,2048)])
box(800,2085,240,74,'Fin',green,terminal=True)
text(800,2180,'Flujo completo coordinado por el orquestador tras registrar la entrevista.',23)
path=Path('output/figures/flujo_generacion_srs.png')
im.save(path,dpi=(300,300))
print(path.resolve())
