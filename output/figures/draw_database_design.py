from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

S=2
W,H=1880,1580
im=Image.new('RGB',(W*S,H*S),'white')
d=ImageDraw.Draw(im)
ink='#253747'
def text(x,y,t,size=25,b=False,mono=False,anchor='mm'):
    name=('consolab.ttf' if b else 'consola.ttf') if mono else ('arialbd.ttf' if b else 'arial.ttf')
    f=ImageFont.truetype('C:/Windows/Fonts/'+name,size*S)
    d.text((x*S,y*S),t,font=f,fill=ink,anchor=anchor)
def entity(x,y,w,title,table,fields):
    h=100+len(fields)*43+15
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),radius=12*S,fill='#F8FAFC',outline=ink,width=2*S)
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+92)*S),radius=12*S,fill='#DFEAF5',outline=ink,width=2*S)
    text(x+w/2,y+30,title,28,True)
    text(x+w/2,y+66,table,24,mono=True)
    for i,(key,name) in enumerate(fields):
        yy=y+120+i*43
        text(x+20,yy,key,21,True,anchor='lm')
        text(x+130,yy,name,25,mono=True,anchor='lm')
    return y+h
def line(points):
    d.line([(x*S,y*S) for x,y in points],fill=ink,width=3*S,joint='curve')

entity(40,95,535,'Contexto académico','project_context',[
('PK / FK','project_id'),('','content'),('','updated_at')])
end=entity(675,95,500,'Proyecto','project',[
('PK','id'),('','name'),('','description'),('','created_at')])
entity(1300,95,540,'Documento SRS','srs_document',[
('PK','id'),('FK','project_id'),('','content'),('','created_at')])
entity(100,650,650,'Entrevista','interview',[
('PK','id'),('FK','project_id'),('','audio_path'),('','transcription'),('','created_at')])
entity(1060,650,740,'Requisito funcional','requirement',[
('PK','id'),('FK','project_id'),('FK','interview_id'),('','code'),('','description'),('','actor'),('','priority'),('','priority_reason'),('','source_excerpt'),('','ambiguity_detected'),('','ambiguity_reason'),('','verifiable'),('','verification_reason'),('','enriched_context *')])
# Numeric cardinalities: each dependent row belongs to exactly one parent.
line([(575,215),(675,215)])
text(602,193,'0..1',22,True);text(652,193,'1',22,True)
line([(1175,215),(1300,215)])
text(1198,193,'1',22,True);text(1268,193,'0..N',22,True)
line([(815,end),(815,480),(425,480),(425,650)])
text(839,end+26,'1',23,True);text(462,625,'0..N',23,True)
text(582,450,'agrupa',23)
line([(1030,end),(1030,515),(1430,515),(1430,650)])
text(1054,end+26,'1',23,True);text(1467,625,'0..N',23,True)
text(1240,484,'reúne',23)
line([(750,848),(1060,848)])
text(773,821,'1',23,True);text(1025,821,'0..N',23,True)
text(905,879,'origina',23)
text(420,1085,'content: contexto guardado como texto JSON.',23)
text(420,1130,'audio_path: referencia al archivo de audio.',23)
text(W/2,1445,'PK: clave primaria · FK: clave foránea · 0..N: cero o varios registros · 0..1: cero o un registro',24)
text(W/2,1490,'* enriched_context es un campo heredado; el contexto actual se almacena en project_context.',23)
text(W/2,1530,'Nombres de tablas y campos correspondientes a los modelos del prototipo.',23)
out=Path(__file__).parent/'diseno_base_datos_prototipo.png'
im.save(out,dpi=(300,300))
print(out.resolve())
