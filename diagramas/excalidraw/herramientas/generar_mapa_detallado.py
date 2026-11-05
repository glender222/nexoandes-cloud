"""Genera el mapa adicional; conserva intacto el editable original. Requiere Pillow."""
import json,copy,base64,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
BOUNDS=json.loads(Path(__file__).with_name('limites_iconos.json').read_text())
E=[]
FILES={}
def common(t,x,y,w,h,**kw):
 i=f'e{len(E):05d}'
 d=dict(id=i,type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor='#243449',backgroundColor='transparent',fillStyle='solid',strokeWidth=1.5,strokeStyle='solid',roughness=0,opacity=100,groupIds=[],frameId=None,roundness=None,seed=1000+len(E),version=1,versionNonce=0,isDeleted=False,boundElements=[],updated=1793836800000,link=None,locked=False)
 d.update(kw);E.append(d);return d

def text(s,x,y,size=20,color='#243449',w=None,align='left'):
 lines=s.split('\n'); from PIL import ImageFont
 font=ImageFont.truetype('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',size)
 width=w or max(font.getlength(l) for l in lines)+2
 return common('text',x,y,width,len(lines)*size*1.25,fontSize=size,fontFamily=2,text=s,originalText=s,textAlign=align,verticalAlign='top',containerId=None,autoResize=True,lineHeight=1.25,strokeColor=color)

def svg_asset(folder,key,x,y,size=64,color=None):
 records=json.loads((BASE/'bibliotecas'/folder/('FUENTES.json' if folder=='complementos' else 'FUENTE.json')).read_text())['iconos']
 record=records[str(key)];raw=(BASE/'bibliotecas'/folder/record['archivo']).read_text()
 if folder=='complementos':
  shade=color or record.get('color','#52667a')
  raw=raw.replace('currentColor',shade)
  if record['autor']=='Simple Icons':raw=raw.replace('<svg ','<svg fill="'+shade+'" ',1)
 data=raw.encode();fid=hashlib.sha256(data).hexdigest()[:40]
 FILES[fid]=dict(id=fid,mimeType='image/svg+xml',dataURL='data:image/svg+xml;base64,'+base64.b64encode(data).decode(),created=1793836800000,lastRetrieved=1793836800000)
 return common('image',x,y,size,size,fileId=fid,status='saved',scale=[1,1],crop=None)

def symbol(idx,x,y,size=30,color=None):return svg_asset('complementos',idx,x,y,size,color)

def sg(x,y,resource):
 e=symbol(2001,x,y,30,'#7950b5');e['customData']={'tipo':'Security Group','recurso':resource};return e

def icon(lib,idx,x,y,size=64):
 if lib=='complementos':return symbol(idx,x,y,size)
 if lib=='aws-arquitectura':
  official=BASE/'bibliotecas'/'aws-oficial'
  record=json.loads((official/'FUENTE.json').read_text())['iconos'].get(str(idx))
  if record:
   raw=(official/record['archivo']).read_bytes();fid=hashlib.sha256(raw).hexdigest()[:40]
   FILES[fid]=dict(id=fid,mimeType='image/svg+xml',dataURL='data:image/svg+xml;base64,'+base64.b64encode(raw).decode(),created=1793836800000,lastRetrieved=1793836800000)
   common('image',x,y,size,size,fileId=fid,status='saved',scale=[1,1],crop=None)
   return
 a=json.loads((BASE/'bibliotecas'/f'{lib}.excalidrawlib').read_text())['libraryItems'][idx]['elements']
 b=BOUNDS[lib][idx];scale=size/max(b[2]-b[0],b[3]-b[1]);gx=f'icon{len(E)}';ox=x+(size-(b[2]-b[0])*scale)/2;oy=y+(size-(b[3]-b[1])*scale)/2
 for raw in a:
  if raw['type']=='text':continue
  d=copy.deepcopy(raw);d.update(id=f'e{len(E):05d}',x=ox+(raw['x']-b[0])*scale,y=oy+(raw['y']-b[1])*scale,width=raw['width']*scale,height=raw['height']*scale,roughness=0,fillStyle='solid',groupIds=[gx],boundElements=[],frameId=None,version=1,versionNonce=0,isDeleted=False,locked=False)
  d.pop('index',None);d.pop('strokeSharpness',None)
  for key in ['startBinding','endBinding','containerId']: 
   if key in d:d[key]=None
  for key in ['points']:
   if key in d:d[key]=[[p[0]*scale,p[1]*scale] for p in d[key]]
  d['strokeWidth']=max(.5,raw.get('strokeWidth',1)*scale)
  E.append(d)
 return gx

def scene():return dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=E,appState=dict(viewBackgroundColor='#ffffff',gridSize=None,zoom={'value':.5}),files=FILES)

# Tarjetas, conectores y textos nativos; SVG oficiales AWS embebidos por icono.
# Azure/GCP: bibliotecas locales. Autorias y condiciones en sus FUENTES.json.
INK='#243449'; MUTED='#52667a'; BLUE='#1768ac'; PURPLE='#7950b5'; GREEN='#248562'; ORANGE='#b96812'
def rect(x,y,w,h,fill='#ffffff',stroke='#ccd6df',dash='solid',sw=1.5):
 return common('rectangle',x,y,w,h,backgroundColor=fill,strokeColor=stroke,strokeStyle=dash,strokeWidth=sw,roundness={'type':3})
def line(points,color=INK,dash='solid',arrow=True,sw=2,role=None,origin=None,target=None):
 x,y=points[0]
 d=common('arrow' if arrow else 'line',x,y,max(p[0] for p in points)-min(p[0] for p in points),max(p[1] for p in points)-min(p[1] for p in points),points=[[a-x,b-y] for a,b in points],strokeColor=color,strokeStyle=dash,strokeWidth=sw,startBinding=None,endBinding=None,lastCommittedPoint=None,startArrowhead=None,endArrowhead='arrow' if arrow else None,elbowed=False)
 if role:d['customData']={'conexion':role,'origen':origin,'destino':target}
 return d
def label(s,x,y,size=18,color=MUTED):
 t=text(s,x+7,y+4,size,color);r=rect(x,y,t['width']+14,t['height']+8,'#ffffff','#ffffff',sw=0);E.remove(r);E.insert(len(E)-1,r)
 return t

def card(x,y,w,h,title,detail,lib=None,idx=None,color=INK,fs=23):
 start=len(E);rect(x,y,w,h,'#ffffff','#c5d2df');offset=20
 if lib:icon(lib,idx,x+18,y+(h-60)/2,60);offset=96
 text(title,x+offset,y+17,fs,color)
 if detail:text(detail,x+offset,y+49,18,MUTED)
 group=f'card{start}'
 for e in E[start:]:e['groupIds'].append(group)


def service(x,y,w,title,detail,lib='aws-arquitectura',idx=78,size=68,fs=23):
 start=len(E)
 icon(lib,idx,x+(w-size)/2,y,size)
 text(title,x,y+size+10,fs,w=w,align='center')
 if detail:text(detail,x,y+size+42,18,MUTED,w=w,align='center')
 group=f'service{start}'
 for e in E[start:]:e['groupIds'].append(group)

def main():
 rect(0,0,2700,1830,'#ffffff','#ffffff',sw=0)
 text('NexoAndes',40,28,43)
 text('Arquitectura multicloud · implementación académica',315,38,30,MUTED)
 text('AWS principal  /  GCP contingencia  /  Azure respaldo',42,88,22,MUTED)
 rect(40,125,2600,4,'#243449','#243449',sw=0)
 text('Inventario: 04/11/2026 · 23:01 Lima',1250,92,18,MUTED)

 # AWS: dos columnas de disponibilidad y capas de subredes alineadas.
 rect(220,165,1490,1390,'#ffffff','#596a7c',sw=2)
 icon('aws-arquitectura',1001,245,183,45)
 text('AWS Cloud · región us-east-1',308,185,29)
 vpc=rect(250,265,1430,985,'#ffffff','#9152bb',sw=2)
 vpc['customData']={'tipo':'AWS VPC','recurso':'nexoandes','cidr':'10.10.0.0/16'}
 icon('aws-arquitectura',1002,267,277,32)
 text('VPC nexoandes · 10.10.0.0/16',315,279,23,PURPLE)
 text('ZONA A · us-east-1a',310,330,24)
 text('ZONA B · us-east-1b',1000,330,24)
 line([(945,322),(945,1110)],'#b3c1cf','dotted',False,1)

 for x,w,cidr in [(300,610,'10.10.1.0/24'),(980,650,'10.10.2.0/24')]:
  rect(x,385,w,215,'#f3f8eb','#a3bf7d')
  icon('aws-arquitectura',1003,x+14,396,28)
  text('Subred pública · '+cidr,x+54,400,20,'#4b6e25')
 for x,w,cidr in [(300,610,'10.10.11.0/24'),(980,650,'10.10.12.0/24')]:
  rect(x,645,w,220,'#edf6fc','#80b7d2')
  icon('aws-arquitectura',1004,x+14,656,28)
  text('Privada APP · '+cidr,x+54,660,20,BLUE)
 rect(300,955,610,190,'#f3eff9','#b4a0cd')
 icon('aws-arquitectura',1004,314,966,28)
 text('Privada DATOS · 10.10.20.0/24',354,970,20,PURPLE)

 # Servicios públicos: símbolos oficiales sin tarjetas alrededor de cada icono.
 service(330,440,190,'NAT Gateway','',idx=217,size=62,fs=22)
 service(670,440,190,'strongSwan','EC2',size=62,fs=22)
 rect(878,431,134,160,'#ffffff','#ffffff',sw=0)
 service(810,442,270,'ALB público','',idx=229,size=68,fs=24)
 text('TLS académico',857,556,16,MUTED,w=175,align='center')
 service(1290,462,220,'Internet Gateway','',idx=215,size=62,fs=22)

 # Un ASG distribuye las web; Supabase queda fuera del ASG.
 asg_start=len(E)
 asg=rect(440,697,805,158,'transparent','#dc871c',dash='dashed')
 asg['customData']={'tipo':'Auto Scaling Group','recurso':'nexoandes-web','minimo':2,'maximo':4}
 icon('aws-arquitectura',88,680,708,28)
 text('Auto Scaling · web 2–4',725,710,17,ORANGE)
 service(450,740,265,'Web A','',size=62,fs=23)
 service(980,740,265,'Web B','',size=62,fs=23)
 for e in E[asg_start:]:e['groupIds'].append('aws-asg-web')
 service(1310,740,290,'Supabase','',lib='complementos',idx=3001,size=54,fs=23)
 text('EC2 · SaaS académico',1310,835,16,MUTED,w=290,align='center')
 sg(1007,550,'alb');sg(825,440,'vpn');sg(1195,810,'app');sg(865,970,'db');sg(1580,740,'supabase')
 icon('aws-arquitectura',68,1500,780,18);symbol(2002,1526,780,18);text('40 GB',1552,781,16,MUTED)

 # PostgreSQL de negocio sobre EC2, no RDS. Datos persistentes separados.
 service(330,1017,255,'PostgreSQL 15','EC2 · primario',lib='complementos',idx=3002,size=58,fs=22)
 service(620,1017,250,'EBS datos','20 GB',idx=68,size=58,fs=22)
 symbol(2002,805,1104,22)
 line([(486,1047),(716,1047)],MUTED,'solid',False,1.5)
 rect(980,955,650,190,'#f5faf7','#bad6c8')
 text('Supabase · componentes',1002,977,24,GREEN)
 for x,idx,name in [(1010,2003,'Auth'),(1110,2004,'REST'),(1210,3002,'PG17'),(1310,2005,'Envoy'),(1410,2006,'Studio'),(1510,2007,'Meta')]:
  symbol(idx,x+12,1025,40);text(name,x,1074,16,w=65,align='center')
 symbol(2003,1005,1110,22);text('Studio · HTTPS 8443',1040,1112,18,MUTED)

 # Usuario externo, flechas de aplicación y conexiones internas.
 service(32,400,150,'Usuarios','',idx=1005,size=65,fs=22)
 line([(184,445),(240,445),(240,433),(840,433),(840,471),(911,471)],BLUE)
 label('HTTPS 443 / 8443',530,439,18,BLUE)
 # Las bajadas rodean los títulos de subred; cada destino recibe una sola punta.
 line([(911,493),(840,493),(840,630),(650,630),(650,725),(582,725),(582,740)],BLUE,role='alb-web-a',origin='ALB',target='Web A')
 line([(979,493),(1050,493),(1050,630),(1305,630),(1305,725),(1112,725),(1112,740)],BLUE,role='alb-web-b',origin='ALB',target='Web B')
 text('HTTP 80 → web',1095,570,16,BLUE)
 line([(979,479),(1070,479),(1070,615),(1648,615),(1648,759),(1482,759)],GREEN,role='alb-supabase',origin='ALB',target='Supabase')
 text('HTTP 8000',1500,570,16,GREEN)
 line([(1143,771),(1290,771)],GREEN,arrow=False,role='web-b-auth',origin='Web B',target='bus Auth')
 line([(614,783),(760,783),(760,885),(1290,885),(1290,771)],GREEN,arrow=False,role='web-a-auth',origin='Web A',target='bus Auth')
 common('ellipse',1287,768,6,6,backgroundColor=GREEN,strokeColor=GREEN,strokeWidth=0)
 line([(1290,771),(1428,771)],GREEN,role='web-auth',origin='web privadas',target='Supabase Auth')
 label('Auth · 8000',1030,870,16,GREEN)
 line([(551,783),(512,783),(512,925),(930,925)],BLUE,arrow=False,role='web-a-pg15',origin='Web A',target='bus PostgreSQL')
 line([(1081,783),(1050,783),(1050,925),(930,925)],BLUE,arrow=False,role='web-b-pg15',origin='Web B',target='bus PostgreSQL')
 common('ellipse',927,922,6,6,backgroundColor=BLUE,strokeColor=BLUE,strokeWidth=0)
 line([(930,925),(930,1009),(455,1009),(455,1017)],BLUE,role='app-pg15',origin='web privadas',target='PostgreSQL 15')
 label('TCP 5432 privado',600,910,17,BLUE)
 # NAT: relación de salida, separada del tráfico de usuarios.
 line([(551,755),(285,755),(285,630),(320,630),(320,471),(394,471)],MUTED,'dotted',False,role='egreso-nat',origin='subredes privadas',target='NAT Gateway')

 # El gateway pertenece a la VPC; el bucket es un servicio regional externo.
 ep_start=len(E)
 endpoint=rect(300,1165,610,70,'#f5f2fa','#b4a0cd')
 endpoint['customData']={'tipo':'S3 Gateway Endpoint','terraform':'aws_vpc_endpoint.s3','parent':vpc['id']}
 icon('aws-arquitectura',219,340,1182,36)
 text('S3 Gateway Endpoint',398,1175,20,PURPLE)
 text('Gateway · rutas privadas',398,1205,16,MUTED)
 for e in E[ep_start:]:e['groupIds'].append('aws-s3-gateway-endpoint')
 bucket_start=len(E)
 bucket=rect(980,1280,700,130,'#f6faf5','#c2d7bd')
 bucket['customData']={'tipo':'Amazon S3','alcance':'regional; fuera de la VPC'}
 icon('aws-arquitectura',74,1030,1300,64)
 text('Amazon S3',1120,1297,24)
 symbol(2002,1120,1340,24);symbol(2011,1164,1340,24);symbol(2012,1208,1340,24)
 text('1 h / 14 d',1250,1343,18,MUTED)
 for e in E[bucket_start:]:e['groupIds'].append('aws-s3-regional')
 line([(455,1145),(455,1165)],ORANGE,'dashed',role='pg15-endpoint',origin='PostgreSQL 15',target='S3 Gateway Endpoint')
 line([(1455,740),(1455,710),(1662,710),(1662,1155),(945,1155),(945,1200),(910,1200)],ORANGE,'dashed',role='supabase-endpoint',origin='Supabase',target='S3 Gateway Endpoint')
 text('Backup Supabase',1465,895,16,ORANGE)
 line([(600,1235),(600,1336),(980,1336)],ORANGE,'dashed',role='endpoint-s3',origin='S3 Gateway Endpoint',target='Amazon S3')
 text('HTTPS 443 privado',620,1355,17,ORANGE)

 # Controles existentes, en una franja regional común.
 rect(250,1445,1430,83,'#f8f4fa','#d4c4de')
 icon('aws-arquitectura',155,280,1460,48)
 text('CloudWatch',350,1460,18)
 icon('aws-arquitectura',192,620,1460,48)
 text('IAM · LabRole',690,1460,18)
 icon('aws-arquitectura',172,970,1460,48)
 text('SSM',1040,1460,18)
 symbol(2001,1295,1460,44,'#7950b5');text('Security Groups',1360,1470,19)

 # GCP: los servicios comparten la VM indicada; su parada afecta a todos ellos.
 rect(1880,165,760,730,'#f8fbff','#4285f4',sw=2)
 icon('gcp-servicios',0,1900,183,56)
 text('Google Cloud · contingencia',1980,185,29,'#2058a6')
 text('us-central1-a',1905,237,19,MUTED)
 rect(1900,280,720,405,'#eef5ff','#a8c5e8')
 text('VPC propia · subred 10.30.1.0/24',1920,296,21,BLUE)
 rect(1920,345,680,245,'#ffffff','#a8c5e8')
 icon('gcp-servicios',21,1940,365,52)
 text('Compute Engine · e2-micro',2010,367,23)
 text('10.30.1.10 · 1 GB RAM',2010,406,18,MUTED)
 for x,idx,name in [(1995,3002,'PG15'),(2215,2005,'IPsec'),(2450,2008,'Portal')]:
  symbol(idx,x,450,44);text(name,x-24,510,19,w=95,align='center')
 symbol(2009,1940,560,22);text('10 + 20 GB',1975,562,18,MUTED)
 rect(1920,610,680,48,'#fff0da','#ecc48b')
 symbol(2010,1940,622,24,'#86510a');text('VM detenida',1980,624,20,'#86510a')
 icon('gcp-servicios',3,1930,730,60)
 text('Cloud Storage',2020,726,25)
 symbol(2002,2020,771,24);symbol(2011,2064,771,24)
 # Conexión IPsec lógica. No es un AWS VPN Gateway administrado.
 line([(796,482),(870,482),(870,605),(1745,605),(1745,430),(1920,430)],PURPLE,'dashed',role='vpn-aws-gcp',origin='strongSwan AWS',target='VM GCP')
 label('IPsec\nUDP 500 / 4500',1736,330,17,PURPLE)
 label('IPsec inactivo',1740,448,16,PURPLE)
 # Replicación PG15 hacia el gateway EC2 de AWS.
 line([(428,1046),(260,1046),(260,605),(690,605),(690,482),(734,482)],PURPLE,'dashed',role='replica-pg15-gateway',origin='PostgreSQL 15',target='strongSwan AWS')
 label('Réplica PG15',280,915,16,PURPLE)

 # Azure: jerarquía real de recursos. La red es hermana del Storage Account.
 az_start=len(E)
 rect(1880,940,760,505,'#f5faff','#1681c4',sw=2)
 text('Azure · respaldo',1905,958,29,'#086aab')
 text('northcentralus',2440,969,18,MUTED)
 rg_start=len(E)
 rg=rect(1900,1015,720,410,'#edf5fc','#9ec3e0')
 rg['customData']={'tipo':'Azure Resource Group','recurso':'nexoandes-lab'}
 svg_asset('azure-oficial','Resource-Groups',1918,1028,30)
 text('nexoandes-lab',1960,1033,22,BLUE)
 storage_start=len(E)
 account=rect(1915,1080,690,215,'#ffffff','#aacde4')
 account['customData']={'tipo':'Azure Storage Account','terraform':'azurerm_storage_account.backup','parent':rg['id']}
 svg_asset('azure-oficial','Storage-Accounts',1930,1094,40)
 text('Storage Account · LRS',1985,1102,23)
 blob_start=len(E)
 container=rect(1935,1150,650,76,'#f3f8fc','#c2d9e9')
 container['customData']={'tipo':'Azure Blob Container','recurso':'postgresql','acceso':'private','parent':account['id']}
 svg_asset('azure-oficial','Blob-Block',1950,1168,40)
 text('postgresql',2010,1160,22)
 text('Contenedor Blob',2010,1193,16,MUTED)
 symbol(2002,2458,1176,26);text('Privado',2494,1180,18,MUTED)
 for e in E[blob_start:]:e['groupIds'].append('azure-blob-container')
 for x,idx,title in [(1950,2011,'Versionado'),(2175,2017,'Borrado 7 d'),(2400,2012,'Retención 14 d')]:
  symbol(idx,x,1250,24);text(title,x+34,1253,17,MUTED)
 for e in E[storage_start:]:e['groupIds'].append('azure-storage-account')
 network_start=len(E)
 vnet=rect(1915,1310,690,100,'#ffffff','#aacde4')
 vnet['customData']={'tipo':'Azure Virtual Network','recurso':'nexoandes-vnet','parent':rg['id']}
 svg_asset('azure-oficial','Virtual-Networks',1930,1330,44)
 text('VNet 10.20.0.0/16',1990,1320,21,BLUE)
 text('GatewaySubnet 10.20.255.0/27',1990,1353,18,MUTED)
 text('VPN Gateway deshabilitado',1990,1381,16,MUTED)
 for e in E[network_start:]:e['groupIds'].append('azure-vnet')
 for e in E[rg_start:]:e['groupIds'].append('azure-resource-group')
 for e in E[az_start:]:e['groupIds'].append('azure-cloud')
 # Flujos lógicos de respaldos, sin laptop en la topología del servicio.
 line([(1680,1345),(1810,1345),(1810,758),(1930,758)],ORANGE,'dashed',role='s3-gcp-copia',origin='S3; copia bajo demanda',target='Cloud Storage')
 line([(1810,1114),(1915,1114)],ORANGE,'dashed',role='s3-azure-copia',origin='copia bajo demanda',target='Azure Storage Account')
 label('HTTPS 443\nBajo demanda',1730,976,17,ORANGE)

 # Leyenda y contexto fuera de las redes.
 rect(40,1600,920,142,'#f4f7fa','#d9e1e8')
 text('Flujos',62,1616,24)
 line([(65,1672),(155,1672)],BLUE);text('Aplicación',175,1659,18)
 line([(440,1672),(530,1672)],PURPLE,'dashed');text('IPsec / réplica inactiva',550,1659,18)
 line([(65,1715),(155,1715)],ORANGE,'dashed');text('Respaldo lógico',175,1702,18)
 line([(440,1715),(530,1715)],MUTED,'dotted',False);text('Salida a Internet',550,1702,18)
 # Una leyenda breve conserva el significado de los controles genéricos.
 for x,idx,title in [(1050,2002,'Privado'),(1250,2011,'Versionado'),(1450,2012,'Retención')]:
  symbol(idx,x,1630,32);text(title,x-35,1680,18,w=110,align='center')
 rect(1880,1600,760,105,'#f4f7fa','#d9e1e8')
 text('Web: 2 AZ + ASG · BD/Auth: 1 VM',1900,1620,22)
 text('DR PG15 manual · Supabase sin réplica',1900,1660,19,MUTED)
 text('Corte fechado · Copias bajo demanda. Especificaciones y pruebas: README del mapa.',42,1783,18,MUTED)
 out=BASE/'nexoandes-multicloud-detallado.excalidraw';out.write_text(json.dumps(scene(),ensure_ascii=False,indent=2)+'\n')
 print(f'{out}: {len(E)} elementos y {len(FILES)} SVG incrustados')
if __name__=='__main__':main()
