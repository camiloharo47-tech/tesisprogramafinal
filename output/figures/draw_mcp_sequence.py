from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
S=2
W,H=1740,1450
im=Image.new('RGB',(W*S,H*S),'white'); d=ImageDraw.Draw(im)
ink='#23364A'; blue='#E9F2FC'; green='#EAF6EF'; amber='#FFF3D9'
def font(size=26,bold=False): return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size*S)
def text(x,y,value,size=26,bold=False):
    lines=value.split('\n'); f=font(size,bold); step=(size+9)*S
    for i,t in enumerate(lines):
        bb=d.textbbox((0,0),t,font=f)
        d.text((x*S-(bb[2]-bb[0])/2,y*S-len(lines)*step/2+i*step),t,fill=ink,font=f)
def box(x,y,w,h,label,fill=blue,size=26):
    d.rounded_rectangle(((x-w/2)*S,(y-h/2)*S,(x+w/2)*S,(y+h/2)*S),radius=10*S,fill=fill,outline=ink,width=2*S)
    text(x,y,label,size)
def stroke(points,dashed=False):
    pts=[(x*S,y*S) for x,y in points]
    if dashed:
        (x1,y1),(x2,y2)=pts; length=math.hypot(x2-x1,y2-y1)
        for k in range(0,int(length),18*S):
            a=k/length;b=min(k+10*S,length)/length
            d.line((x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b),fill=ink,width=2*S)
    else:d.line(pts,fill=ink,width=3*S)
def arrow(x1,x2,y,label,dashed=False):
    stroke([(x1,y),(x2,y)],dashed)
    sign=1 if x2>x1 else -1
    d.polygon([(x2*S,y*S),((x2-sign*13)*S,(y-6)*S),((x2-sign*13)*S,(y+6)*S)],fill=ink)
    text((x1+x2)/2,y-29,label,24)
xs=[190,630,1070,1510]
headers=['Agente solicitante','Cliente MCP','Servidor MCP','Servicio o\nalmacenamiento']
for x,t in zip(xs,headers):
    stroke([(x,143),(x,1240)],True)
    box(x,85,340,112,t,size=28)
text(1510,181,'Crossref / SQLite / Ollama',23)
arrow(190,630,260,'1. Solicitar operación')
box(630,350,365,92,'2. Configurar servidor\nStdioServerParameters',amber,25)
arrow(630,1070,480,'3. Abrir contexto Client\ne iniciar servidor por stdio')
arrow(630,1070,615,'4. Invocar call_tool\n(nombre y argumentos)')
arrow(1070,1510,750,'5. Ejecutar operación')
arrow(1510,1070,865,'6. Devolver datos o fallo',True)
arrow(1070,630,975,'7. Respuesta MCP\n(contenido estructurado o error)',True)
box(630,1065,360,84,'8. Comprobar is_error\ny recuperar el contenido',amber,24)
arrow(630,1070,1160,'9. Cerrar contexto Client')
arrow(630,190,1280,'10. Entregar resultado\no propagar excepción',True)
box(1070,1370,1120,78,'Cada llamada abre su propio contexto de comunicación.\nEl servidor utilizado depende de la herramienta solicitada.',green,24)
out=Path('output/figures/secuencia_comunicacion_mcp.png'); im.save(out,dpi=(300,300));print(out.resolve())
