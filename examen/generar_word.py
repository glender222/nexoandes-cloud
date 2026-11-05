import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_exam_document():
    doc = docx.Document()

    # Page Margins (Normal 2.54 cm / 1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        # Header / Footer setup
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Examen Práctico Integrador — Cloud Computing | Glender Vargas")
        f_run.font.name = "Calibri"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(120, 144, 156)

    # Styling constants
    COLOR_PRIMARY = RGBColor(27, 54, 93)     # #1B365D Navy Blue
    COLOR_SECONDARY = RGBColor(0, 115, 187)  # #0073BB AWS Blue
    COLOR_DARK = RGBColor(35, 47, 62)        # #232F3E Charcoal
    COLOR_MUTED = RGBColor(100, 116, 139)    # #64748B Slate Gray
    HEX_PRIMARY = "1B365D"
    HEX_LIGHT_BG = "F4F7FA"
    HEX_BORDER = "CBD5E1"
    HEX_ALT_ROW = "F8FAFC"

    def set_cell_margins(cell, top=80, bottom=80, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def prevent_row_split(table):
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    def add_custom_heading(text, level=1):
        p = doc.add_paragraph()
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Calibri"
        if level == 1:
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(5)
            run.font.size = Pt(15)
            run.font.color.rgb = COLOR_PRIMARY
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="3" w:color="{HEX_PRIMARY}"/></w:pBdr>')
            p._p.get_or_add_pPr().append(pBdr)
        elif level == 2:
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            run.font.size = Pt(12)
            run.font.color.rgb = COLOR_SECONDARY
        elif level == 3:
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            run.font.size = Pt(10.5)
            run.font.color.rgb = COLOR_DARK
        return p

    def add_body_p(text="", bold_prefix="", space_after=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.name = "Calibri"
            r_bold.font.size = Pt(10)
            r_bold.font.color.rgb = COLOR_DARK
        if text:
            r_text = p.add_run(text)
            r_text.font.name = "Calibri"
            r_text.font.size = Pt(10)
            r_text.font.color.rgb = COLOR_DARK
        return p

    def add_callout(question_title, answer_text, space_after_box=4):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.7)
        prevent_row_split(tbl)
        
        cell = tbl.cell(0, 0)
        set_cell_background(cell, HEX_LIGHT_BG)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="20" w:space="0" w:color="{HEX_PRIMARY}"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        ''')
        cell._tc.get_or_add_tcPr().append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_q = p.add_run(question_title + "\n")
        r_q.bold = True
        r_q.font.name = "Calibri"
        r_q.font.size = Pt(10)
        r_q.font.color.rgb = COLOR_PRIMARY
        
        r_a = p.add_run(answer_text)
        r_a.font.name = "Calibri"
        r_a.font.size = Pt(9.5)
        r_a.font.color.rgb = COLOR_DARK
        
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(space_after_box)

    def add_image_evidence(img_path, caption_text, width_inches=6.2):
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_path} not found")
            return
        
        tbl = doc.add_table(rows=2, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.7)
        prevent_row_split(tbl)
        
        # Row 0: Image
        cell_img = tbl.cell(0, 0)
        set_cell_background(cell_img, "FFFFFF")
        set_cell_margins(cell_img, top=40, bottom=20, left=40, right=40)
        p_img = cell_img.paragraphs[0]
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(0)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_inches))
        
        # Row 1: Caption
        cell_cap = tbl.cell(1, 0)
        set_cell_background(cell_cap, HEX_LIGHT_BG)
        set_cell_margins(cell_cap, top=30, bottom=40, left=80, right=80)
        p_cap = cell_cap.paragraphs[0]
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(0)
        run_cap = p_cap.add_run(caption_text)
        run_cap.italic = True
        run_cap.font.name = "Calibri"
        run_cap.font.size = Pt(8.5)
        run_cap.font.color.rgb = COLOR_MUTED
        
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>
            </w:tcBorders>
        ''')
        cell_img._tc.get_or_add_tcPr().append(borders)
        
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)

    # ==========================================
    # PÁGINA 1: PORTADA
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(14)
    p_inst.paragraph_format.space_after = Pt(2)
    r_uni = p_inst.add_run("UNIVERSIDAD PERUANA UNIÓN\n")
    r_uni.bold = True
    r_uni.font.name = "Calibri"
    r_uni.font.size = Pt(16)
    r_uni.font.color.rgb = COLOR_PRIMARY
    
    r_fac = p_inst.add_run("Facultad de Ingeniería y Arquitectura · Escuela Profesional de Ingeniería de Sistemas\n")
    r_fac.font.name = "Calibri"
    r_fac.font.size = Pt(11)
    r_fac.font.color.rgb = COLOR_MUTED
    
    r_cur = p_inst.add_run("CURSO: CLOUD COMPUTING — PROYECTO INTEGRADOR")
    r_cur.bold = True
    r_cur.font.name = "Calibri"
    r_cur.font.size = Pt(12)
    r_cur.font.color.rgb = COLOR_SECONDARY

    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(12)
    p_sep.paragraph_format.space_after = Pt(18)
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="18" w:space="1" w:color="{HEX_PRIMARY}"/></w:pBdr>')
    p_sep._p.get_or_add_pPr().append(pBdr)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(4)
    r_t1 = p_title.add_run("EXAMEN PRÁCTICO INTEGRADOR\n")
    r_t1.bold = True
    r_t1.font.name = "Calibri"
    r_t1.font.size = Pt(22)
    r_t1.font.color.rgb = COLOR_PRIMARY
    
    r_t2 = p_title.add_run("Contenidos hasta la Semana 7 — Implementación en AWS")
    r_t2.font.name = "Calibri"
    r_t2.font.size = Pt(13.5)
    r_t2.font.color.rgb = COLOR_DARK

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(4)
    p_sub.paragraph_format.space_after = Pt(30)
    r_sub = p_sub.add_run("Caso de Evaluación: InnovaTech Perú — Servidor Web Seguro y Almacenamiento Desacoplado")
    r_sub.italic = True
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = COLOR_MUTED

    tbl_meta = doc.add_table(rows=6, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    tbl_meta.columns[0].width = Inches(2.2)
    tbl_meta.columns[1].width = Inches(4.5)
    prevent_row_split(tbl_meta)
    
    meta_rows = [
        ("ESTUDIANTE:", "Glender Vargas"),
        ("CÓDIGO:", "[Completar código de estudiante]"),
        ("DOCENTE:", "Asin Gomez Fernando Manuel"),
        ("FECHA:", "22 / 10 / 2026"),
        ("PLATAFORMA:", "AWS Academy Learner Lab (Amazon Web Services)"),
        ("PUNTAJE:", "________ / 20 puntos")
    ]
    for i, (label, val) in enumerate(meta_rows):
        c0 = tbl_meta.cell(i, 0)
        c1 = tbl_meta.cell(i, 1)
        bg = HEX_LIGHT_BG if i % 2 == 0 else "FFFFFF"
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=70, bottom=70, left=110, right=110)
        set_cell_margins(c1, top=70, bottom=70, left=110, right=110)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(10.5)
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = "Calibri"
        r1.font.size = Pt(10.5)
        if i == 0 or i == 2:
            r1.bold = True
            r1.font.color.rgb = COLOR_DARK
        elif i == 5:
            r1.bold = True
            r1.font.color.rgb = COLOR_SECONDARY
        else:
            r1.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # ==========================================
    # PÁGINA 2: PARTE 1. DISEÑO DE ARQUITECTURA
    # ==========================================
    add_custom_heading("PARTE 1. Diseño de Arquitectura (3 puntos)", level=1)
    
    add_body_p(
        "Para responder a los requerimientos de la empresa InnovaTech Perú, se diseñó e implementó una solución integral "
        "en Amazon Web Services (AWS) que publica de manera segura un servidor web Linux Apache, respaldado por volúmenes en bloque EBS "
        "y desacoplando la gestión de documentos y copias de seguridad mediante almacenamiento de objetos Amazon S3. "
        "Toda la infraestructura opera dentro de una Virtual Private Cloud (VPC) dedicada, con enrutamiento explícito a Internet "
        "y protección perimetral mediante Security Groups."
    )

    add_custom_heading("1.1 Diagrama Lógico de Arquitectura", level=2)
    add_image_evidence("examen/diagrama_arquitectura.png", "Diagrama 1: Arquitectura de infraestructura implementada en AWS para el caso InnovaTech Perú.", width_inches=6.3)

    add_custom_heading("1.2 Respuestas Técnicas de Arquitectura", level=2)
    
    add_callout(
        "1. ¿Por qué la instancia EC2 necesita una dirección IP pública para este escenario?",
        "En esta arquitectura de nivel inicial de migración, la instancia EC2 aloja el servidor web directamente en una subred pública "
        "sin disponer de un Application Load Balancer intermedio. Por tanto, la dirección IPv4 pública es estrictamente indispensable para que "
        "los clientes desde Internet puedan alcanzar el servidor. El Internet Gateway (IGW) realiza una traducción de direcciones de red 1:1 "
        "(NAT uno a uno) entre la IP pública enrutable y la dirección IP privada interna (10.20.10.6), posibilitando la negociación TCP "
        "y el tráfico bidireccional en el puerto web 80."
    )

    add_callout(
        "2. ¿Cuál es la diferencia entre almacenar archivos del servidor en EBS y almacenarlos en S3?",
        "• Amazon EBS (Elastic Block Store): Es almacenamiento a nivel de bloques (block storage) de ultra baja latencia, acoplado directamente "
        "a la instancia EC2 como su disco duro local dentro de una Zona de Disponibilidad específica. Requiere un sistema de archivos tradicional (XFS/ext4) "
        "y es indispensable para el sistema operativo, binarios y librerías de ejecución; no obstante, su ciclo de vida y alcance están vinculados a la instancia.\n"
        "• Amazon S3 (Simple Storage Service): Es almacenamiento de objetos desacoplado, independiente del estado del servidor y accesible mediante API/HTTP. "
        "Ofrece redundancia geográfica nativa en múltiples Zonas de Disponibilidad con una durabilidad del 99.999999999% (11 nueves). Es ideal para "
        "documentos corporativos, activos multimedia y respaldos, garantizando que los datos subsistan incluso si el servidor EC2 es terminado."
    )

    add_callout(
        "3. Clasifique los recursos implementados en cómputo, red, almacenamiento y seguridad.",
        "• Cómputo: Instancia Amazon EC2 (EXAMEN-GLENDERVARGAS-WEB, tipo t3.micro, 2 vCPUs, 1 GiB RAM, SO Amazon Linux 2023).\n"
        "• Red: Amazon VPC (EXAMEN-GLENDERVARGAS-VPC, CIDR 10.20.0.0/16), Subred Pública (EXAMEN-GLENDERVARGAS-SUBNET-PUB, CIDR 10.20.10.0/24), "
        "Internet Gateway (EXAMEN-GLENDERVARGAS-IGW), Tabla de Rutas (EXAMEN-GLENDERVARGAS-RT con ruta 0.0.0.0/0 ➔ IGW) y Asignación de IPv4 Pública.\n"
        "• Almacenamiento: Volumen en Bloque Amazon EBS (EXAMEN-GLENDERVARGAS-WEB-ROOT, 8 GiB gp3, cifrado) y Bucket Amazon S3 (examen-cloud-gv-849533029543).\n"
        "• Seguridad: Security Group (EXAMEN-GLENDERVARGAS-SG, filtrado estatal de puertos 80 y 22), S3 Block Public Access (4 reglas de bloqueo activas) y Key Pair SSH (vockey)."
    )

    doc.add_page_break()

    # ==========================================
    # PÁGINA 3: PARTE 2. IMPLEMENTACIÓN DE RED AWS
    # ==========================================
    add_custom_heading("PARTE 2. Implementación de Red AWS (4 puntos)", level=1)
    
    add_body_p(
        "Se construyó una topología de red virtual totalmente aislada, cumpliendo con la exigencia de no utilizar únicamente la VPC Default. "
        "La red se configuró con un direccionamiento IP privado estricto (10.20.0.0/16) y se dotó de conectividad hacia Internet mediante un Internet Gateway y una tabla de enrutamiento asociada."
    )

    tbl_net = doc.add_table(rows=5, cols=4)
    tbl_net.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_net.autofit = False
    tbl_net.columns[0].width = Inches(1.5)
    tbl_net.columns[1].width = Inches(2.3)
    tbl_net.columns[2].width = Inches(1.6)
    tbl_net.columns[3].width = Inches(1.3)
    prevent_row_split(tbl_net)
    
    headers_net = ["Componente", "Nombre de Recurso", "Identificador AWS", "Configuración"]
    for j, h in enumerate(headers_net):
        cell = tbl_net.cell(0, j)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    net_data = [
        ("VPC", "EXAMEN-GLENDERVARGAS-VPC", "vpc-0e549a023b818b322", "10.20.0.0/16"),
        ("Subnet Pública", "EXAMEN-GLENDERVARGAS-SUBNET-PUB", "subnet-0d4b5ad045ac91b41", "10.20.10.0/24 (AZ 1a)"),
        ("Internet Gateway", "EXAMEN-GLENDERVARGAS-IGW", "igw-0ef3e59c3749996a8", "Attached a VPC"),
        ("Route Table", "EXAMEN-GLENDERVARGAS-RT", "rtb-09c9e6226272af29b", "0.0.0.0/0 ➔ IGW")
    ]
    for i, row in enumerate(net_data, start=1):
        for j, val in enumerate(row):
            cell = tbl_net.cell(i, j)
            bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(4)

    add_custom_heading("2.1 Evidencias de Red", level=2)
    add_image_evidence("examen/image.png", "Figura 1: Mapa de recursos de la VPC EXAMEN-GLENDERVARGAS-VPC mostrando la conectividad hacia la subred pública, tabla de rutas e Internet Gateway.", width_inches=6.3)
    add_image_evidence("examen/image-1.png", "Figura 2: Detalle de la subred EXAMEN-GLENDERVARGAS-SUBNET-PUB (10.20.10.0/24) con asignación automática de IPv4 pública habilitada (Auto-assign public IPv4 address: Yes).", width_inches=6.3)
    
    doc.add_page_break()

    # PÁGINA 4: Continuación de Red (Figuras 3 y 4)
    add_image_evidence("examen/image-2.png", "Figura 3: Internet Gateway EXAMEN-GLENDERVARGAS-IGW (igw-0ef3e59c3749996a8) en estado Attached a la VPC del examen.", width_inches=6.3)
    add_image_evidence("examen/image-3.png", "Figura 4: Tabla de Rutas EXAMEN-GLENDERVARGAS-RT evidenciando la regla por defecto 0.0.0.0/0 apuntando al IGW y su asociación a la subred.", width_inches=6.3)

    # ==========================================
    # PÁGINA 5: PARTE 3. SERVIDOR EC2 Y PUBLICACIÓN WEB
    # ==========================================
    doc.add_page_break()
    add_custom_heading("PARTE 3. Servidor EC2 y Publicación Web (5 puntos)", level=1)
    
    add_body_p(
        "Se desplegó una instancia Amazon EC2 basada en Amazon Linux 2023 (AL2023 x86_64), de tipo t3.micro, "
        "asociada a la subred pública y protegida mediante el Security Group EXAMEN-GLENDERVARGAS-SG. "
        "A través del script de inicialización UserData se ejecutó la instalación, habilitación y arranque automatizado "
        "del servidor web Apache HTTPD (dnf install httpd -y, systemctl enable httpd, systemctl start httpd), "
        "creando la página index.html con los datos del estudiante Glender Vargas y el caso de evaluación."
    )

    tbl_ec2 = doc.add_table(rows=5, cols=4)
    tbl_ec2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_ec2.autofit = False
    tbl_ec2.columns[0].width = Inches(1.6)
    tbl_ec2.columns[1].width = Inches(2.2)
    tbl_ec2.columns[2].width = Inches(1.6)
    tbl_ec2.columns[3].width = Inches(1.3)
    prevent_row_split(tbl_ec2)
    
    headers_ec2 = ["Parámetro", "Valor Configurado", "Identificador AWS", "Estado"]
    for j, h in enumerate(headers_ec2):
        cell = tbl_ec2.cell(0, j)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    ec2_data = [
        ("Instancia EC2", "EXAMEN-GLENDERVARGAS-WEB", "i-00dcab0a251d51e69", "Running (t3.micro)"),
        ("Dirección IPv4 Pública", "44.204.139.138", "Asignada por IGW", "Accesible vía Internet"),
        ("Dirección IPv4 Privada", "10.20.10.6", "Subred pública 10.20.10.0/24", "Activa"),
        ("Security Group", "EXAMEN-GLENDERVARGAS-SG", "sg-082c010b7e988d4f5", "Inbound: 80 y 22")
    ]
    for i, row in enumerate(ec2_data, start=1):
        for j, val in enumerate(row):
            cell = tbl_ec2.cell(i, j)
            bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_DARK

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(4)

    add_custom_heading("3.1 Justificación de las Reglas del Security Group", level=2)
    add_body_p(
        "• Regla Inbound HTTP (Puerto 80 / TCP / Origen 0.0.0.0/0): Es estrictamente requerida para que cualquier usuario o cliente "
        "desde Internet pueda establecer una conexión web HTTP con el servidor Apache y visualizar el catálogo informativo de InnovaTech Perú.\n"
        "• Regla Inbound SSH (Puerto 22 / TCP / Origen 0.0.0.0/0): Permite la conexión administrativa segura de consola remota para gestión, soporte técnico y diagnóstico del sistema operativo.\n"
        "• Regla Outbound (Todo el tráfico / 0.0.0.0/0): Permite que el servidor descargue parches de seguridad y paquetes desde los repositorios oficiales de Amazon Linux mediante dnf."
    )

    add_custom_heading("3.2 Evidencias de Cómputo y Servicio Web", level=2)
    add_image_evidence("examen/image-4.png", "Figura 5: Instancia EC2 EXAMEN-GLENDERVARGAS-WEB (i-00dcab0a251d51e69) en estado Running con IPv4 pública 44.204.139.138 e IPv4 privada 10.20.10.6.", width_inches=6.3)
    
    doc.add_page_break()

    # PÁGINA 6: Continuación de Cómputo (Figuras 6 y 7)
    add_image_evidence("examen/image-5.png", "Figura 6: Security Group EXAMEN-GLENDERVARGAS-SG (sg-082c010b7e988d4f5) mostrando las reglas de entrada para los puertos 80 (HTTP) y 22 (SSH).", width_inches=6.3)
    add_image_evidence("examen/image-6.png", "Figura 7: Navegador web accediendo exitosamente mediante la IPv4 pública a la página del examen con el nombre del estudiante Glender Vargas y datos institucionales.", width_inches=5.8)

    # ==========================================
    # PÁGINA 7: PARTE 4. AMAZON S3 Y SEGURIDAD
    # ==========================================
    doc.add_page_break()
    add_custom_heading("PARTE 4. Amazon S3 y Seguridad (4 puntos)", level=1)
    
    add_body_p(
        "Se implementó un bucket de almacenamiento de objetos independiente denominado examen-cloud-gv-849533029543 en la región us-east-1. "
        "Conforme a las directrices de seguridad de AWS, se mantuvo habilitado de forma estricta el Bloqueo de Acceso Público (Block Public Access) "
        "en sus cuatro niveles. Se estructuraron los prefijos documentos/, evidencias/ y backup/, cargando en cada uno los archivos respectivos del caso de evaluación."
    )

    add_custom_heading("4.1 Respuestas Técnicas de S3 y Seguridad", level=2)
    
    add_callout(
        "4. ¿Por qué no es una buena práctica hacer público todo el bucket para compartir un solo archivo?",
        "Hacer público todo el bucket vulnera el principio de mínimo privilegio (least privilege) y expone indiscriminadamente todos los objetos "
        "existentes y futuros que se almacenen en él. Esto genera severos riesgos de fuga de información confidencial, alteración o borrado malicioso "
        "y costos no previstos por transferencia de datos saliente. La buena práctica consiste en mantener el bucket 100% privado y generar URLs prefirmadas "
        "(pre-signed URLs) con un tiempo de expiración limitado (por ejemplo, 15 minutos) únicamente para el archivo específico que se desea compartir."
    )

    add_callout(
        "5. Si EC2 necesitara acceso permanente al bucket, ¿conviene almacenar Access Key/Secret Key en el servidor o utilizar un IAM Role? Justifique.",
        "Conviene enfáticamente utilizar un IAM Role adjunto a la instancia mediante un Instance Profile. Guardar credenciales estáticas (Access Key y Secret Key) "
        "en archivos locales o variables de entorno representa una vulnerabilidad crítica ante accesos no autorizados al servidor o inspección del código. "
        "Un IAM Role elimina los secretos estáticos, proporcionando credenciales temporales criptográficas que AWS renueva automáticamente a través del "
        "Instance Metadata Service (IMDSv2), garantizando trazabilidad, auditoría en CloudTrail y mínimo privilegio sin riesgo de filtración."
    )

    add_custom_heading("4.2 Evidencias de Amazon S3", level=2)
    add_image_evidence("examen/image-7.png", "Figura 8: Bucket Amazon S3 examen-cloud-gv-849533029543 mostrando la organización por prefijos (/backup/, /documentos/ y /evidencias/).", width_inches=4.5)
    add_image_evidence("examen/image-8.png", "Figura 9: Configuración de seguridad del bucket S3 confirmando Block all public access en estado ON con las cuatro restricciones aplicadas.", width_inches=4.5)

    # ==========================================
    # PÁGINA 8: PARTE 5. VALIDACIÓN Y DIAGNÓSTICO
    # ==========================================
    doc.add_page_break()
    add_custom_heading("PARTE 5. Validación y Diagnóstico (2 puntos)", level=1)
    
    add_body_p(
        "Se ejecutaron pruebas de conectividad y disponibilidad tanto a nivel local en el servidor como de manera remota desde Internet a través de curl. "
        "El servidor Apache respondió inmediatamente con código de estado HTTP/1.1 200 OK y las cabeceras correspondientes, confirmando la operatividad del servicio."
    )

    add_custom_heading("5.1 Pregunta Técnica de Diagnóstico", level=2)
    add_callout(
        "6. Si EC2 está Running pero la página no abre desde Internet, indique cuatro elementos concretos de AWS/Linux que revisaría para diagnosticar el problema:",
        "1. Reglas de Entrada del Security Group (Inbound Rules): Verificar que exista una regla activa que permita el tráfico TCP en el puerto 80 con origen 0.0.0.0/0.\n"
        "2. Tabla de Rutas y Enrutamiento al Internet Gateway: Comprobar que la subred de la instancia esté vinculada a una tabla de rutas con la regla por defecto 0.0.0.0/0 apuntando al IGW en estado 'Active'.\n"
        "3. Estado del Servicio Apache en Linux: Conectarse por consola y ejecutar 'sudo systemctl status httpd' para verificar que el servicio esté 'active (running)' y escuchando en el puerto ('ss -tulpn | grep :80').\n"
        "4. Asignación de Dirección IPv4 Pública: Confirmar que la instancia posea efectivamente una IPv4 pública asignada y no únicamente una IP privada interna."
    )

    add_custom_heading("5.2 Evidencia de Diagnóstico y Validación", level=2)
    add_image_evidence("examen/image-9.png", "Figura 10: Validación técnica de conectividad mediante terminal ejecutando curl -I http://44.204.139.138 con respuesta satisfactoria HTTP/1.1 200 OK de Apache.", width_inches=4.8)

    # ==========================================
    # PÁGINA 9: PARTE 6. ANÁLISIS PROFESIONAL
    # ==========================================
    doc.add_page_break()
    add_custom_heading("PARTE 6. Análisis Profesional (2 puntos)", level=1)
    add_body_p("A continuación se presentan las fundamentaciones técnicas a los cuestionamientos estratégicos planteados (máximo 6 líneas por respuesta):", space_after=6)

    add_callout(
        "7. La empresa desea migrar posteriormente una base de datos local. Explique dos riesgos que deberían evaluarse antes de la migración.",
        "Primero, el tiempo de inactividad (downtime) y el riesgo de pérdida o inconsistencia transaccional durante la ventana de corte (cutover) final.\n"
        "Segundo, la seguridad y latencia del enlace de red; alojar la base de datos sin una subred privada estrictamente aislada o con una conexión inestable hacia la sede física degrada el rendimiento de las consultas y expone información confidencial a accesos no autorizados."
    )

    add_callout(
        "8. Explique qué responsabilidad corresponde a AWS y cuál al cliente respecto a la seguridad de la instancia EC2.",
        "Bajo el Modelo de Responsabilidad Compartida, AWS asume la «seguridad DE la nube»: protección física de los centros de datos, servidores anfitriones, virtualización y hardware.\n"
        "El cliente asume la «seguridad EN la nube»: aplicar parches y actualizaciones al sistema operativo (Amazon Linux), configurar las reglas del firewall (Security Groups), asegurar el servicio web Apache, gestionar el par de llaves SSH y administrar los permisos de acceso."
    )

    add_callout(
        "9. Si el servidor recibe miles de solicitudes simultáneas, ¿qué limitación presenta la arquitectura implementada?",
        "La arquitectura presenta un punto único de falla (SPOF) y un cuello de botella de recursos fijos.\n"
        "Al depender de una única máquina virtual t3.micro en una sola Zona de Disponibilidad, la capacidad de CPU, memoria y ancho de banda se satura rápidamente bajo concurrencia masiva, agotando la cola de conexiones de Apache y provocando denegación de servicio (latencia extrema o caída total) sin capacidad de autorrecuperación."
    )

    add_callout(
        "10. Proponga dos mejoras para aumentar disponibilidad, seguridad o escalabilidad.",
        "1. Alta Disponibilidad y Escalabilidad Horizontal: Implementar un Application Load Balancer (ALB) público que distribuya el tráfico entre múltiples instancias EC2 gestionadas por un Auto Scaling Group (ASG), distribuidas en al menos dos Zonas de Disponibilidad (Multi-AZ).\n"
        "2. Seguridad Perimetral y Protección Web: Reubicar las instancias en subredes privadas dejando únicamente el balanceador en la subred pública, e integrar AWS WAF junto con certificados SSL/TLS (HTTPS) para mitigar ataques DDoS, inyecciones SQL y cifrar el tráfico en tránsito."
    )

    # ==========================================
    # PÁGINA 10: CONCLUSIONES, FIRMA Y RÚBRICA
    # ==========================================
    doc.add_page_break()
    add_custom_heading("7. Conclusiones Técnicas", level=1)
    
    add_body_p(
        "1. Aislamiento y Control Mediante Redes Virtuales Personalizadas: La creación de una VPC propia (10.20.0.0/16) con subredes públicas y tablas de rutas específicas valida la importancia de no depender de la VPC Default para despliegues empresariales. Esto garantiza un perímetro de seguridad controlado, segmentación de red limpia y un control estricto del tráfico entrante y saliente a través del Internet Gateway.",
        bold_prefix="• "
    )
    add_body_p(
        "2. Desacoplamiento Arquitectónico entre Cómputo y Almacenamiento: La separación entre el almacenamiento en bloque (Amazon EBS) para el sistema operativo y el almacenamiento de objetos (Amazon S3) para documentos y respaldos incrementa drásticamente la resiliencia operativa de InnovaTech Perú. Los activos de negocio permanecen resguardados con durabilidad de 11 nueves con independencia del ciclo de vida de los servidores web.",
        bold_prefix="• "
    )
    add_body_p(
        "3. Aplicación del Principio de Mínimo Privilegio y Seguridad Integral: La configuración de Security Groups restringidos exclusivamente a los servicios requeridos (HTTP y SSH), la activación irrestricta de Block Public Access en Amazon S3 y la adopción de IAM Roles en lugar de credenciales fijas consolidan una postura de seguridad robusta, conforme a las mejores prácticas del AWS Well-Architected Framework.",
        bold_prefix="• "
    )

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(16)
    p_sig.paragraph_format.space_after = Pt(2)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_sig.add_run("____________________________________________________\n")
    r_line.font.name = "Calibri"
    r_line.font.size = Pt(11)
    r_line.font.color.rgb = COLOR_DARK
    
    r_signame = p_sig.add_run("Firma del Estudiante: Glender Vargas\n")
    r_signame.bold = True
    r_signame.font.name = "Calibri"
    r_signame.font.size = Pt(10.5)
    r_signame.font.color.rgb = COLOR_PRIMARY
    
    r_sigdoc = p_sig.add_run("Estudiante de Ingeniería de Sistemas — Universidad Peruana Unión")
    r_sigdoc.font.name = "Calibri"
    r_sigdoc.font.size = Pt(9)
    r_sigdoc.font.color.rgb = COLOR_MUTED

    p_sp_end = doc.add_paragraph()
    p_sp_end.paragraph_format.space_before = Pt(10)
    p_sp_end.paragraph_format.space_after = Pt(2)

    add_custom_heading("Tabla Oficial de Calificación del Examen", level=2)
    add_body_p("Matriz de evaluación para calificación directa del docente:")

    tbl_rub = doc.add_table(rows=7, cols=4)
    tbl_rub.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_rub.autofit = False
    tbl_rub.columns[0].width = Inches(2.2)
    tbl_rub.columns[1].width = Inches(2.6)
    tbl_rub.columns[2].width = Inches(0.9)
    tbl_rub.columns[3].width = Inches(1.0)
    prevent_row_split(tbl_rub)
    
    headers_rub = ["Criterio de Evaluación", "Evidencia Esperada", "Puntaje Máx.", "Puntaje Obt."]
    for j, h in enumerate(headers_rub):
        cell = tbl_rub.cell(0, j)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rub_data = [
        ("Diseño y comprensión arquitectónica", "Diagrama correcto y respuestas fundamentadas", "3 pts", ""),
        ("Red AWS", "VPC, subnet, IGW y routing funcionales", "4 pts", ""),
        ("Cómputo y publicación web", "EC2 correctamente desplegado y sitio web funcional", "5 pts", ""),
        ("Almacenamiento y seguridad", "S3 configurado y controles básicos aplicados", "4 pts", ""),
        ("Validación y diagnóstico", "Pruebas y diagnóstico técnico fundamentado", "2 pts", ""),
        ("Análisis profesional", "Justificación y propuestas técnicas estratégicas", "2 pts", "")
    ]
    for i, row in enumerate(rub_data, start=1):
        for j, val in enumerate(row):
            cell = tbl_rub.cell(i, j)
            bg = HEX_ALT_ROW if i % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=40, bottom=40, left=70, right=70)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if j == 2:
                r.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r.font.color.rgb = COLOR_DARK

    output_docx = "examen/VARGAS_GLENDER_EXAMEN_CLOUD.docx"
    doc.save(output_docx)
    print(f"Documento Word guardado exitosamente: {output_docx}")

if __name__ == "__main__":
    create_exam_document()
