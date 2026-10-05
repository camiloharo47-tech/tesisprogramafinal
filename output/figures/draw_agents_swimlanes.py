from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

S=2
W,H=2460,1410
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
ink='#263747'
def text(x,y,t,size=23,b=False):
    f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',size*S)
    lines=t.split('\n'); step=size+7
    for i,l in enumerate(lines):
        d.text((x*S,(y-(len(lines)-1)*step/2+i*step)*S),l,font=f,fill=ink,anchor='mm')
def box(x,y,t,w=310,h=88,fill='#FFFFFF',term=False,size=23):
    d.rounded_rectangle(((x-w/2)*S,(y-h/2)*S,(x+w/2)*S,(y+h/2)*S),radius=(h/2 if term else 10)*S,fill=fill,outline=ink,width=2*S)
    text(x,y,t,size)
def arrow(pts,label=None,lx=0,ly=0):
    d.line([(x*S,y*S) for x,y in pts],fill=ink,width=2*S)
    x,y=pts[-1]; px,py=pts[-2]; a=math.atan2(y-py,x-px)
    d.polygon([(x*S,y*S),((x-11*math.cos(a-.5))*S,(y-11*math.sin(a-.5))*S),((x-11*math.cos(a+.5))*S,(y-11*math.sin(a+.5))*S)],fill=ink)
    if label: text(lx,ly,label,20,True)
def diamond(x,y,t):
    d.polygon([(x*S,(y-65)*S),((x+125)*S,y*S),(x*S,(y+65)*S),((x-125)*S,y*S)],fill='#FFF3DA',outline=ink,width=2*S)
    text(x,y,t,22)
xs=[260,745,1230,1715,2200]
heads=['Orquestador','Agente 1\nTranscripción','Agente 2\nRequisitos funcionales','Agente 3\nEnriquecimiento académico','Agente 4\nGeneración del SRS']
for i,(x,h) in enumerate(zip(xs,heads)):
    l=x-232
    d.rectangle((l*S,40*S,(l+464)*S,1250*S),fill=('#F5F7FA' if i==0 else '#F3F7FC' if i<3 else '#F2F8F4'),outline='#A4B1BD',width=S)
    d.rectangle((l*S,40*S,(l+464)*S,150*S),fill='#E1EAF3',outline='#A4B1BD',width=S)
    text(x,90,h,26,True)
    text(x,168,'Coordinación' if i==0 else 'Por entrevista' if i<3 else 'Por proyecto',18,True)

# The hand-off lines occupy the gaps between lanes.
def handoff(x,y,nx):
    mid=(x+nx)/2
    arrow([(x+155,y),(mid,y),(mid,230),(nx-155,230)])

x=xs[0]
box(x,230,'Solicitud de\nprocesamiento completo',term=True)
arrow([(x,274),(x,326)])
box(x,370,'Validar entrevista y\nobtener el proyecto')
arrow([(x,414),(x,476)])
box(x,520,'Iniciar la ejecución\nsecuencial de los agentes')
handoff(x,520,xs[1])
box(x,1080,'Si ocurre un error\nno resuelto, detener\nlas etapas posteriores.',h=124,fill='#FCEDEA',size=22)
text(x,1180,'Se conservan los resultados\nya almacenados.',21)

x=xs[1]
box(x,230,'Consultar el audio\nde la entrevista')
arrow([(x,274),(x,315)])
diamond(x,380,'¿Audio\ndisponible?')
arrow([(x+125,380),(x+170,380),(x+170,474)],'No',x+153,355)
box(x+140,510,'Informar\nerror y parar',w=170,h=72,fill='#FCEDEA',term=True,size=20)
arrow([(x,445),(x,601)],'Sí',x-23,478)
box(x,645,'Transcribir en español\ncon Whisper')
arrow([(x,689),(x,761)])
box(x,805,'Comprobar que\nel texto no esté vacío')
arrow([(x,849),(x,956)])
box(x,1000,'Guardar la transcripción')
handoff(x,1000,xs[2])

x=xs[2]
box(x,230,'Leer y segmentar\nla transcripción')
arrow([(x,274),(x,336)])
box(x,380,'Seleccionar segmentos\ncon posibles funcionalidades')
arrow([(x,424),(x,496)])
box(x,540,'Extraer candidatos\ncon el modelo de lenguaje')
arrow([(x,584),(x,656)])
box(x,700,'Comprobar respaldo\ny descartar duplicados')
arrow([(x,744),(x,816)])
box(x,860,'Registrar actor, prioridad\ne indicadores de calidad')
arrow([(x,904),(x,956)])
box(x,1000,'Guardar los RF aceptados\ny su evidencia de origen')
handoff(x,1000,xs[3])

x=xs[3]
box(x,230,'Consultar los datos y\nlos RF del proyecto')
arrow([(x,274),(x,315)])
diamond(x,380,'¿Existen RF?')
arrow([(x+125,380),(x+170,380),(x+170,474)],'No',x+153,355)
box(x+140,510,'Informar\nerror y parar',w=170,h=72,fill='#FCEDEA',term=True,size=20)
arrow([(x,445),(x,576)],'Sí',x-23,478)
box(x,620,'Buscar en Crossref y\nseleccionar publicaciones')
arrow([(x,664),(x,705)])
diamond(x,770,'¿Evidencia\nsuficiente?')
arrow([(x-125,770),(x-132,770),(x-132,906)],'Sí',x-153,814)
arrow([(x+125,770),(x+132,770),(x+132,906)],'No',x+157,814)
box(x-112,950,'Sintetizar y\ncomprobar\nlos aportes',w=202,h=88,size=21)
box(x+112,950,'Registrar que\nno hay contexto\nrespaldado',w=202,h=88,size=21)
arrow([(x-112,994),(x-112,1035),(x,1035),(x,1076)])
arrow([(x+112,994),(x+112,1035),(x,1035)],None)
box(x,1120,'Guardar el resultado\nacadémico del proyecto')
handoff(x,1120,xs[4])

x=xs[4]
box(x,230,'Recuperar todos los RF\ny el contexto disponible')
arrow([(x,274),(x,356)])
box(x,400,'Organizar el documento\ncon estructura IEEE 830')
arrow([(x,444),(x,526)])
box(x,570,'Conservar los RF\ny su evidencia de origen')
arrow([(x,614),(x,696)])
box(x,740,'Completar otros apartados\ncomo orientación fuera\ndel alcance de la tesis',h=110,size=22)
arrow([(x,795),(x,876)])
box(x,920,'Guardar el documento SRS')
arrow([(x,964),(x,1066)])
box(x,1110,'SRS disponible\npara consulta',term=True,fill='#E3F0E7')

text(W/2,1300,'Las flechas indican el orden de ejecución. El intercambio de información se apoya en los datos almacenados.',23)
text(W/2,1345,'RF: requisitos funcionales. Cada rombo representa una decisión del proceso.',22)
out=Path(__file__).parent/'actividades_agentes_carriles.png'
im.save(out,dpi=(300,300))
print(out.resolve())
