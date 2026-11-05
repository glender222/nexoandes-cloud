from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
img = Image.new('RGB', (W, H), color='#F8FAFC')
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype('DejaVuSans-Bold.ttf', 30)
    font_sec = ImageFont.truetype('DejaVuSans-Bold.ttf', 18)
    font_bold = ImageFont.truetype('DejaVuSans-Bold.ttf', 15)
    font_reg = ImageFont.truetype('DejaVuSans.ttf', 14)
    font_small = ImageFont.truetype('DejaVuSans.ttf', 12)
except:
    font_title = ImageFont.load_default()
    font_sec = font_title
    font_bold = font_title
    font_reg = font_title
    font_small = font_title

# Header Banner
draw.rounded_rectangle([30, 20, W-30, 85], radius=10, fill='#1B365D')
draw.text((50, 36), 'ARQUITECTURA DE INFRAESTRUCTURA AWS — CASO INNOVATECH PERÚ', font=font_title, fill='#FFFFFF')

# AWS Cloud Container
draw.rounded_rectangle([30, 105, W-30, H-25], radius=16, fill='#FFFFFF', outline='#FF9900', width=3)
draw.rounded_rectangle([45, 115, 420, 155], radius=6, fill='#FF9900')
draw.text((55, 125), 'AWS Cloud — Región us-east-1 (N. Virginia)', font=font_bold, fill='#FFFFFF')

# Left side: Internet & Client
draw.rounded_rectangle([50, 280, 220, 380], radius=10, fill='#E2E8F0', outline='#94A3B8', width=2)
draw.text((65, 298), 'Usuario / Cliente', font=font_sec, fill='#1E293B')
draw.text((75, 335), 'Navegador Web', font=font_reg, fill='#475569')

draw.rounded_rectangle([50, 460, 220, 560], radius=10, fill='#E2E8F0', outline='#94A3B8', width=2)
draw.text((85, 480), 'Internet', font=font_sec, fill='#1E293B')
draw.text((60, 515), 'Tráfico Público IPv4', font=font_reg, fill='#475569')

# Internet Gateway
draw.rounded_rectangle([260, 420, 480, 530], radius=10, fill='#7C3AED', outline='#6D28D9', width=2)
draw.text((290, 435), 'Internet Gateway', font=font_bold, fill='#FFFFFF')
draw.text((275, 465), 'EXAMEN-GLENDERVARGAS-IGW', font=font_small, fill='#EDE9FE')
draw.text((285, 492), 'igw-0ef3e59c3749996a8', font=font_small, fill='#DDD6FE')

# Arrow Client/Internet -> IGW
draw.line([(220, 510), (260, 475)], fill='#2563EB', width=4)
draw.polygon([(260, 475), (248, 468), (248, 482)], fill='#2563EB')
draw.text((222, 470), 'HTTP (80)', font=font_small, fill='#2563EB')

# VPC Container
draw.rounded_rectangle([520, 170, 1480, 1010], radius=14, fill='#F0FDF4', outline='#16A34A', width=3)
draw.rounded_rectangle([540, 185, 1100, 230], radius=6, fill='#16A34A')
draw.text((555, 195), 'VPC: EXAMEN-GLENDERVARGAS-VPC  |  CIDR: 10.20.0.0/16', font=font_bold, fill='#FFFFFF')

# Route Table Box
draw.rounded_rectangle([540, 250, 1460, 335], radius=8, fill='#FFFFFF', outline='#86EFAC', width=2)
draw.text((560, 262), 'Tabla de Rutas: EXAMEN-GLENDERVARGAS-RT (rtb-09c9e6226272af29b)', font=font_bold, fill='#166534')
draw.text((560, 295), '• Ruta local: 10.20.0.0/16 ➔ local          • Ruta Internet: 0.0.0.0/0 ➔ igw-0ef3e59c3749996a8', font=font_reg, fill='#334155')

# Arrow IGW -> VPC / RT
draw.line([(480, 475), (520, 475)], fill='#7C3AED', width=4)

# Public Subnet Container
draw.rounded_rectangle([540, 360, 1460, 990], radius=12, fill='#EFF6FF', outline='#3B82F6', width=3)
draw.rounded_rectangle([560, 375, 1360, 415], radius=6, fill='#3B82F6')
draw.text((575, 385), 'Subnet Pública: EXAMEN-GLENDERVARGAS-SUBNET-PUB | 10.20.10.0/24 (AZ us-east-1a)', font=font_bold, fill='#FFFFFF')
draw.text((575, 428), 'Auto-assign Public IPv4: Yes  |  Asociada a EXAMEN-GLENDERVARGAS-RT', font=font_small, fill='#1E40AF')

# Security Group Container
draw.rounded_rectangle([560, 460, 1440, 970], radius=10, fill='#FFFFFF', outline='#DC2626', width=2)
draw.rounded_rectangle([580, 472, 1180, 510], radius=6, fill='#DC2626')
draw.text((595, 482), 'Security Group: EXAMEN-GLENDERVARGAS-SG (sg-082c010b7e988d4f5)', font=font_bold, fill='#FFFFFF')

draw.text((595, 524), 'Reglas Inbound:   [TCP 80 / HTTP ➔ 0.0.0.0/0]     [TCP 22 / SSH ➔ 0.0.0.0/0]', font=font_small, fill='#991B1B')

# EC2 Instance Box
draw.rounded_rectangle([580, 555, 1420, 805], radius=10, fill='#FEF3C7', outline='#D97706', width=2)
draw.text((605, 572), 'Instancia EC2: EXAMEN-GLENDERVARGAS-WEB (i-00dcab0a251d51e69)', font=font_sec, fill='#92400E')
draw.text((605, 610), '• Tipo: t3.micro (2 vCPU, 1 GiB RAM)          • SO: Amazon Linux 2023 (AL2023)', font=font_reg, fill='#78350F')
draw.text((605, 642), '• IPv4 Pública: 44.204.139.138                • IPv4 Privada: 10.20.10.6', font=font_bold, fill='#1E3A8A')
draw.text((605, 674), '• Servicio Web: Apache HTTPD 2.4.69 (Puerto 80 ACTIVO)', font=font_reg, fill='#065F46')
draw.text((605, 706), '• DocumentRoot: /var/www/html/index.html (Página Informativa Activa)', font=font_small, fill='#475569')
draw.text((605, 736), '  Título: EXAMEN CLOUD COMPUTING | Estudiante: Glender Vargas | Fecha: 22/10/2026', font=font_small, fill='#1E293B')

# EBS Volume Box
draw.rounded_rectangle([580, 825, 1420, 945], radius=8, fill='#F1F5F9', outline='#64748B', width=2)
draw.text((605, 842), 'Amazon EBS: EXAMEN-GLENDERVARGAS-WEB-ROOT (vol-010041d8e6ba04a8b)', font=font_bold, fill='#334155')
draw.text((605, 875), '• Tipo: gp3 | Tamaño: 8 GiB | Punto de montaje: /dev/xvda (Volumen raíz del SO)', font=font_reg, fill='#475569')
draw.text((605, 908), '• Almacenamiento a nivel de bloques para el sistema operativo | Cifrado por defecto', font=font_small, fill='#64748B')

# S3 Bucket Container (Right Side)
draw.rounded_rectangle([1510, 170, 1890, 1010], radius=14, fill='#FEF9C3', outline='#CA8A04', width=3)
draw.rounded_rectangle([1525, 185, 1875, 255], radius=8, fill='#CA8A04')
draw.text((1545, 197), 'Almacenamiento S3', font=font_sec, fill='#FFFFFF')
draw.text((1535, 227), 'examen-cloud-gv-849533029543', font=font_small, fill='#FEF08A')

# Block public access badge
draw.rounded_rectangle([1525, 275, 1875, 350], radius=6, fill='#DC2626')
draw.text((1545, 290), 'Block Public Access: ON', font=font_bold, fill='#FFFFFF')
draw.text((1540, 318), '(4/4 Reglas de Bloqueo Activas)', font=font_small, fill='#FEE2E2')

# S3 Folders
draw.rounded_rectangle([1525, 370, 1875, 540], radius=8, fill='#FFFFFF', outline='#EAB308', width=2)
draw.text((1545, 388), 'Prefijo: /documentos/', font=font_bold, fill='#854D0E')
draw.text((1545, 418), 'politica_seguridad_innovatech.txt', font=font_small, fill='#334155')
draw.text((1545, 458), 'Prefijo: /evidencias/', font=font_bold, fill='#854D0E')
draw.text((1545, 488), 'evidencia_despliegue_arquitectura.txt', font=font_small, fill='#334155')

draw.rounded_rectangle([1525, 560, 1875, 700], radius=8, fill='#FFFFFF', outline='#EAB308', width=2)
draw.text((1545, 578), 'Prefijo: /backup/', font=font_bold, fill='#854D0E')
draw.text((1545, 608), 'respaldo_configuracion_web.txt', font=font_small, fill='#334155')
draw.text((1545, 650), 'Durabilidad: 99.999999999%', font=font_small, fill='#16A34A')

# S3 Security Note
draw.rounded_rectangle([1525, 720, 1875, 980], radius=8, fill='#FFFFFF', outline='#94A3B8', width=1)
draw.text((1545, 738), 'Buenas Prácticas S3:', font=font_bold, fill='#1E293B')
draw.text((1540, 775), '• Bucket privado sin exposición.', font=font_small, fill='#475569')
draw.text((1540, 810), '• Compartir vía Pre-signed URLs', font=font_small, fill='#475569')
draw.text((1540, 832), '  con expiración temporal.', font=font_small, fill='#475569')
draw.text((1540, 875), '• Acceso EC2 vía IAM Role', font=font_small, fill='#475569')
draw.text((1540, 898), '  (Instance Profile) sin guardar', font=font_small, fill='#475569')
draw.text((1540, 920), '  claves Access Key locales.', font=font_small, fill='#475569')

# Arrow EC2 -> S3
draw.line([(1420, 680), (1510, 680)], fill='#CA8A04', width=4)
draw.polygon([(1510, 680), (1495, 672), (1495, 688)], fill='#CA8A04')
draw.text((1430, 655), 'IAM / API', font=font_small, fill='#854D0E')

img.save('examen/diagrama_arquitectura.png', 'PNG')
print('Diagrama 1920x1080 generado con éxito!')
