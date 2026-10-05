from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

S=2
W,H=2100,1330
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
ink='#253747'
def text(x,y,t,size=25,b=False):
    f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',size*S)
    ls=t.split('\n'); step=size+10
    for i,l in enumerate(ls):
        d.text((x*S,(y+(i-(len(ls)-1)/2)*step)*S),l,font=f,fill=ink,anchor='mm')
def box(x,y,w,h,fill):
    d.rounded_rectangle(((x-w/2)*S,(y-h/2)*S,(x+w/2)*S,(y+h/2)*S),radius=16*S,fill=fill,outline=ink,width=2*S)
def arrow(pts,dash=False):
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        if dash:
            dist=math.hypot(x2-x1,y2-y1)
            for start in range(0,int(dist),20):
                end=min(start+11,dist)
                d.line(((x1+(x2-x1)*start/dist)*S,(y1+(y2-y1)*start/dist)*S,(x1+(x2-x1)*end/dist)*S,(y1+(y2-y1)*end/dist)*S),fill=ink,width=2*S)
        else:
            d.line((x1*S,y1*S,x2*S,y2*S),fill=ink,width=2*S)
    x,y=pts[-1]; px,py=pts[-2]; a=math.atan2(y-py,x-px)
    d.polygon([(x*S,y*S),((x-13*math.cos(a-.45))*S,(y-13*math.sin(a-.45))*S),((x-13*math.cos(a+.45))*S,(y-13*math.sin(a+.45))*S)],fill=ink)

box(1120,105,1600,130,'#DFEAF9')
text(1120,80,'PRODUCT BACKLOG',30,True)
text(1120,127,'18 elementos: funcionalidades y tareas técnicas del prototipo',26)
arrow([(1120,170),(1120,225)])
box(1120,275,1600,100,'#FFF2CD')
text(1120,275,'Planificación del sprint: selección de tareas y definición del entregable',27,True)
xs=[370,745,1120,1495,1870]
colors=['#E2EFDA','#DFEAF9','#E3F0ED','#FFF0D9','#EDE3F3']
titles=['Configuración\ny transcripción','Extracción de RF y\norquestador inicial','MCP y enriquecimiento\nacadémico','Generación\ndel documento SRS','Interfaz, integración\ny pruebas']
details=['Entorno y datos iniciales\nCarga de audio\nTranscripción con Whisper','Extracción con Ollama\nValidación y evidencia\nConexión entre agentes','Cliente y servidores MCP\nConsulta en Crossref\nContexto por proyecto','Estructura IEEE 830\nPersistencia del SRS\nExportación a Word','Interfaz web completa\nIntegración de los agentes\nPruebas de funcionamiento']
ids=['PB-01 a PB-04','PB-05 a PB-07','PB-08 a PB-11','PB-12 a PB-15','PB-16 a PB-18']
outs=['Entrevistas registradas\ny transcripción\ndisponible','Requisitos almacenados\ncon evidencia\nde la entrevista','Contexto académico\ndel proyecto o registro\nde evidencia insuficiente','Documento SRS\nalmacenado y\nexportable a Word','Prototipo integrado\ny listo para\nevaluación']
# Each column summarizes an iteration; the note below clarifies chronological execution.
arrow([(1120,325),(1120,360)])
d.line((xs[0]*S,360*S,xs[-1]*S,360*S),fill=ink,width=2*S)
for i,x in enumerate(xs):
    arrow([(x,360),(x,405)])
    box(x,560,340,310,colors[i])
    text(x,440,f'SPRINT {i+1}',29,True)
    text(x,500,titles[i],24,True)
    text(x,599,details[i],22)
    text(x,688,ids[i],20)
    arrow([(x,715),(x,760)])
    box(x,845,340,170,colors[i])
    text(x,788,f'Incremento {i+1}',25,True)
    text(x,861,outs[i],23)
    arrow([(x,930),(x,990)])
box(1120,1045,1840,110,'#F7DFDF')
text(1120,1023,'Revisión del incremento y ajustes al backlog',29,True)
text(1120,1067,'Comprobar el funcionamiento, identificar pendientes y preparar la siguiente iteración',24)
arrow([(200,1045),(100,1045),(100,275),(320,275)],dash=True)
text(106,671,'',20)
arrow([(1120,1100),(1120,1155)])
box(1120,1205,1100,100,'#E2EECB')
text(1120,1187,'Al completar los cinco sprints',24,True)
text(1120,1225,'Prototipo funcional listo para la evaluación del capítulo IV',26)
text(1120,1300,'Organización propuesta. Los sprints se desarrollan de forma sucesiva; cada incremento se revisa antes de continuar.',21)
out=Path(__file__).parent/'organizacion_cinco_sprints.png'
im.save(out,dpi=(300,300))
print(out.resolve())
