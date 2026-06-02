import os
import io
import datetime
import streamlit as st

# Intentar cargar librerías con manejo de errores limpio
try:
    from google import genai
    from google.genai import errors
except ImportError:
    st.error("Falta la librería 'google-genai'. Por favor, asegúrate de que esté en tu archivo requirements.txt.")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    st.error("Falta la librería 'reportlab'. Por favor, asegúrate de que esté en tu archivo requirements.txt.")

# Configuración de página de Streamlit para Móvil y Desktop
st.set_page_config(
    page_title="LocalRank Consulting - G-Maps SEO Auditor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para un look premium y oscuro en móviles (S23 Ultra)
st.markdown("""
    <style>
        .reportview-container {
            background: #0B0B0F;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }
        div[data-testid="stExpander"] {
            background-color: #12121A !important;
            border: 1px solid #1F2937 !important;
            border-radius: 8px !important;
        }
        /* Estilos específicos para unificar editores */
        .stTextArea textarea {
            background-color: #0C0C0F !important;
            color: #F3F4F6 !important;
            font-family: 'Consolas', monospace !important;
            font-size: 14px !important;
            border: 1px solid #1F2937 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if "reporte_auditoria" not in st.session_state:
    st.session_state.reporte_auditoria = ""
if "reporte_entregables" not in st.session_state:
    st.session_state.reporte_entregables = ""
if "datos_negocio" not in st.session_state:
    st.session_state.datos_negocio = {}

# --- LÓGICA DE CÁLCULO CIENTÍFICO ---
def calcular_metricas(checklist, fotos, búsquedas, ticket):
    score_gbp = 0
    if checklist["propiedad"] == "Reclamada y Verificada": score_gbp += 8
    if checklist["pin"] == "Correcto (En la entrada)": score_gbp += 8
    if checklist["horarios"] == "Actualizados": score_gbp += 6
    if checklist["categoria"] == "Correctas y específicas": score_gbp += 8
    if checklist["nombre"] == "Limpio y legal (Sin Spam)": score_gbp += 6
    
    score_onpage = 16 if checklist["nap"] == "Consistente" else 0
    
    score_resenas = 0
    if checklist["frecuencia"] == "Flujo constante activo": score_resenas += 5
    if checklist["seo_respuestas"] == "Respuestas con SEO local": score_resenas += 5
    if checklist["crisis"] == "Gestión profesional y comercial": score_resenas += 5
    
    score_comportamiento = 0
    if checklist["chat"] == "Activado y ágil": score_comportamiento += 2
    if checklist["contacto"] == "Enlace optimizado": score_comportamiento += 3
    if checklist["faqs"] == "Configuradas (3-5 FAQs)": score_comportamiento += 2
    
    score_fotos = 0
    total_fotos = sum(fotos.values())
    if total_fotos >= 50: score_fotos += 13
    elif total_fotos >= 20: score_fotos += 8
    else: score_fotos += 3
    
    score_total = score_gbp + score_onpage + score_resenas + score_comportamiento + score_fotos
    
    # Ecuación de Costo de Inacción
    tc = 0.30  # Conversión en México
    ingresos_optimo = búsquedas * 0.06 * tc * ticket
    ingresos_actuales = búsquedas * 0.015 * tc * ticket
    fuga_mensual = ingresos_optimo - ingresos_actuales
    
    if score_total < 45:
        plan_rec = "Plan Básico - Fundamentos y SEO Local ($3,500 MXN pago único)"
    elif score_total <= 75:
        plan_rec = "Plan Avanzado - Implementación e Infraestructura ($6,500 MXN pago único)"
    else:
        plan_rec = "Plan Recurrente - Gestión y Blindaje Mensual ($4,500 MXN / mes)"
        
    return {
        "score": score_total,
        "score_gbp": round((score_gbp / 36.0) * 100, 1),
        "score_onpage": round((score_onpage / 16.0) * 100, 1),
        "score_resenas": round((score_resenas / 15.0) * 100, 1),
        "score_behavior": round((score_comportamiento / 7.0) * 100, 1),
        "score_photos": round((score_fotos / 13.0) * 100, 1),
        "ingresos_optimo": round(ingresos_optimo, 2),
        "ingresos_actuales": round(ingresos_actuales, 2),
        "fuga_mensual": round(fuga_mensual, 2),
        "plan_recomendado": plan_rec
    }

# --- DISEÑO DEL PDF CORPORATIVO ---
def generar_pdf_bytes(texto_contenido, datos_negocio, tipo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=50,
        bottomMargin=50
    )
    
    if tipo == "auditoria":
        primary_color = colors.HexColor("#1E3A8A")
        secondary_color = colors.HexColor("#DC2626")
        doc_titulo = "PLAN DE OPTIMIZACIÓN ALGORÍTMICA Y CAPTACIÓN LOCAL"
        doc_subtitulo = "Auditoría de Visibilidad Comercial y Costo de la Inacción (Preventa)"
    else:
        primary_color = colors.HexColor("#111827")
        secondary_color = colors.HexColor("#059669")
        doc_titulo = "PLAN DE IMPLEMENTACIÓN Y ENTREGABLES OPERATIVOS"
        doc_subtitulo = "Dossier de Activos Técnicos Listos para Integración Directa (Posventa)"

    text_dark = colors.HexColor("#1F2937")
    border_light = colors.HexColor("#E5E7EB")
    bg_panel = colors.HexColor("#F9FAFB")

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        alignment=TA_CENTER,
        spaceAfter=25
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
        leftIndent=15,
        firstLineIndent=-8,
        spaceAfter=4
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=text_dark
    )

    meta_val_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor("#374151")
    )

    story = []

    # Portada Elegante
    story.append(Spacer(1, 40))
    story.append(Paragraph("LOCALRANK CONSULTING", ParagraphStyle('PortLogo', fontName='Helvetica-Bold', fontSize=14, textColor=secondary_color, alignment=TA_CENTER, spaceAfter=20)))
    story.append(Spacer(1, 60))
    story.append(Paragraph(doc_titulo, ParagraphStyle('PortTitle', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=primary_color, alignment=TA_CENTER, spaceAfter=10)))
    story.append(Paragraph(doc_subtitulo, ParagraphStyle('PortSub', fontName='Helvetica', fontSize=12, leading=15, textColor=colors.HexColor("#4B5563"), alignment=TA_CENTER)))
    story.append(Spacer(1, 100))
    
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    fotos_info = f"Interior: {datos_negocio['fotos']['interior']} | Exterior: {datos_negocio['fotos']['exterior']} | Equipo: {datos_negocio['fotos']['equipo']} | Prod/Serv: {datos_negocio['fotos']['productos']} | Logo: {datos_negocio['fotos']['logo_portada']}"
    
    if tipo == "auditoria":
        tabla_portada_data = [
            [Paragraph("PREPARADO PARA:", meta_label_style), Paragraph(datos_negocio.get('nombre', 'N/A'), meta_val_style)],
            [Paragraph("GIRO COMERCIAL:", meta_label_style), Paragraph(datos_negocio.get('giro', 'N/A'), meta_val_style)],
            [Paragraph("SCORE LOCAL:", meta_label_style), Paragraph(f"<b>{datos_negocio['metricas']['score']}/100</b> (Calificación Moz Local)", meta_val_style)],
            [Paragraph("FUGA DE FACTURACIÓN:", meta_label_style), Paragraph(f"<b>${datos_negocio['metricas']['fuga_mensual']:,} MXN</b> / mensuales", ParagraphStyle('RedMeta', parent=meta_val_style, textColor=colors.HexColor("#DC2626")))],
            [Paragraph("FIRMA CONSULTORA:", meta_label_style), Paragraph("<b>LocalRank Consulting</b> (Alejandro Trejo)", meta_val_style)],
            [Paragraph("FECHA DE EMISIÓN:", meta_label_style), Paragraph(fecha_actual, meta_val_style)],
        ]
    else:
        tabla_portada_data = [
            [Paragraph("PREPARADO PARA:", meta_label_style), Paragraph(datos_negocio.get('nombre', 'N/A'), meta_val_style)],
            [Paragraph("GIRO COMERCIAL:", meta_label_style), Paragraph(datos_negocio.get('giro', 'N/A'), meta_val_style)],
            [Paragraph("ACTIVOS DE PLAN:", meta_label_style), Paragraph(datos_negocio['metricas']['plan_recomendado'].split(" - ")[0], meta_val_style)],
            [Paragraph("ESTADO DE ACCESO:", meta_label_style), Paragraph("<b>Solución Desbloqueada (Fase de Implementación)</b>", ParagraphStyle('GreenMeta', parent=meta_val_style, textColor=colors.HexColor("#059669")))],
            [Paragraph("FIRMA CONSULTORA:", meta_label_style), Paragraph("<b>LocalRank Consulting</b> (Alejandro Trejo)", meta_val_style)],
            [Paragraph("FECHA DE EMISIÓN:", meta_label_style), Paragraph(fecha_actual, meta_val_style)],
        ]
    
    t_portada = Table(tabla_portada_data, colWidths=[150, 350])
    t_portada.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_panel),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, border_light)
    ]))
    
    story.append(t_portada)
    story.append(PageBreak())

    # Procesamiento del cuerpo
    lineas = texto_contenido.split("\n")
    elementos_seccion = []
    
    for linea in lineas:
        linea_strip = linea.strip()
        if not linea_strip:
            continue
        
        linea_sana = linea_strip.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        while "**" in linea_sana:
            linea_sana = linea_sana.replace("**", "<b>", 1).replace("**", "</b>", 1)
        
        is_header = False
        for selector in ["Sección", "Seccion", "SECCIÓN", "###", "##"]:
            if linea_sana.startswith(selector) or (linea_sana.isupper() and len(linea_sana) < 45 and any(kw in linea_sana for kw in ["RESEÑA", "FOTO", "SEO", "CATEGOR", "DIAGNÓSTICO", "DIAGNOSTICO", "PROPUESTA", "CONVERSIÓN", "INACCIÓN", "PLAN", "ENTREGABLE", "DOSSIER", "SOLUCIÓN"])):
                is_header = True
                break
        
        if is_header:
            if elementos_seccion:
                story.append(KeepTogether(elementos_seccion))
                elementos_seccion = []
            
            titulo_limpio = linea_sana.replace("#", "").strip()
            elementos_seccion.append(Spacer(1, 10))
            elementos_seccion.append(Paragraph(titulo_limpio, section_heading))
            
            linea_decorativa = Table([[""]], colWidths=[520], rowHeights=[1.5])
            linea_decorativa.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), secondary_color),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            elementos_seccion.append(linea_decorativa)
            elementos_seccion.append(Spacer(1, 8))
        else:
            if linea_sana.startswith("-") or linea_sana.startswith("*") or (len(linea_sana) > 2 and linea_sana[0].isdigit() and linea_sana[1] == "."):
                texto_final = linea_sana.lstrip("-* ").strip()
                if linea_sana[0].isdigit() and linea_sana[1] == ".":
                    texto_final = linea_sana
                elementos_seccion.append(Paragraph(f"• {texto_final}", bullet_style))
            else:
                elementos_seccion.append(Paragraph(linea_sana, body_style))

    if elementos_seccion:
        story.append(KeepTogether(elementos_seccion))

    def add_page_number(canvas, doc):
        if canvas.getPageNumber() == 1:
            return
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 7.5)
        canvas.setFillColor(colors.HexColor("#4B5563"))
        canvas.setStrokeColor(border_light)
        canvas.setLineWidth(0.5)
        canvas.line(45, 42, letter[0] - 45, 42)
        canvas.drawString(45, 28, "LocalRank Consulting | Plan Estratégico de Evolución Local CDMX 2026")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 45, 28, f"Página {page_num}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer.getvalue()

# --- INTERFAZ WEB DE STREAMLIT ---
st.title("🎯 LocalRank Consulting")
st.subheader("G-Maps Local SEO Auditor & Diagnostic Tool")

# Panel lateral de Configuración de API Key
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key_input = st.text_input("Gemini API Key:", type="password", value="")
    st.info("La API Key ingresada se mantendrá segura y protegida en tu sesión local.")

# --- FORMULARIO IZQUIERDO ---
col_form, col_res = st.columns([45, 55])

with col_form:
    st.markdown("### 1. Información General")
    nombre_negocio = st.text_input("Nombre del Negocio o Enlace de Google Maps:", placeholder="Ej: Dental Center Guadalajara")
    
    giro_comercial = st.selectbox(
        "Giro Comercial del Establecimiento:",
        [
            "Salud (Clínicas, Consultorios, Hospitales)",
            "Gastronomía (Restaurantes, Cafeterías, Bares)",
            "Servicios Profesionales B2B (Corporativos, Despachos)",
            "Ocio, Turismo y Entretenimiento (Atracciones, Hoteles)"
        ]
    )
    
    cat_principal = st.text_input("Categoría Principal de Maps:", placeholder="Ej: Clínica dental")
    cat_secundarias = st.text_input("Subcategorías actuales (separadas por comas):", placeholder="Ej: Dentista, Ortodoncista")

    st.markdown("### 2. Ecuación Financiera")
    col_busq, col_tick = st.columns(2)
    with col_busq:
        busquedas_est = st.number_input("Búsquedas Mensuales (Zona):", min_value=1, value=1500, step=100)
    with col_tick:
        ticket_prom = st.number_input("Ticket Promedio ($MXN):", min_value=1.0, value=1200.0, step=50.0)

    # Diagnóstico de Listas de Verificación
    st.markdown("### 3. Diagnóstico de Captación (CTM)")
    
    with st.expander("Bloque 1: Propiedad y Visibilidad"):
        propiedad_ficha = st.selectbox("Propiedad de la Ficha:", ["Reclamada y Verificada", "Sin reclamar / Abandonada"])
        consistencia_nap = st.selectbox("Consistencia NAP (Nombre/Dir/Tel):", ["Consistente", "Datos distintos en Web/Ficha"])
        pin_ubicacion = st.selectbox("Pin de Ubicación Geográfica:", ["Correcto (En la entrada)", "Desplazado / Incorrecto"])
        horarios_reales = st.selectbox("Horarios y Días Festivos:", ["Actualizados", "Obsoletos / Sin festivos"])

    with st.expander("Bloque 2: Arquitectura SEO"):
        cat_optimizacion = st.selectbox("Optimización de Categorías:", ["Correctas y específicas", "Muy genéricas / Erróneas / Faltantes"])
        nombre_spam = st.selectbox("Nombre Comercial Limpio:", ["Limpio y legal (Sin Spam)", "Spam / Keyword stuffing"])
        catalogo_servicios = st.selectbox("Catálogo de Servicios:", ["Completo y redactado", "Vacío / Solo títulos sin descripción"])

    with st.expander("Bloque 3: Canales de Conversión"):
        chat_nativo = st.selectbox("Botón de Chat Nativo GBP:", ["Activado y ágil", "Desactivado / Abandonado"])
        contacto_rapido = st.selectbox("Enlace de Contacto Rápido (WhatsApp/Web):", ["Enlace optimizado", "Link roto / No tiene"])
        faqs_config = st.selectbox("Preguntas Frecuentes (FAQs):", ["Configuradas (3-5 FAQs)", "Vacío / Abandonado"])

    with st.expander("Bloque 4: Prominencia"):
        calidad_visual = st.selectbox("Calidad Visual Reciente:", ["Actualizadas y profesionales", "Fotos viejas / De stock"])
        frecuencia_resenas = st.selectbox("Frecuencia de Reseñas 5 Estrellas:", ["Flujo constante activo", "Sin reseñas recientes / Estancado"])
        seo_respuestas = st.selectbox("SEO en Respuestas de Reseñas:", ["Respuestas con SEO local", "\"Gracias\" plano / Sin responder"])
        gestion_crisis = st.selectbox("Gestión de Crisis (Reseñas 1 Estrella):", ["Gestión profesional y comercial", "Respuestas reactivas / Ignoradas"])

    with st.expander("Inventario de Fotos (Cantidades)"):
        f_interior = st.number_input("Fotos de Interior:", min_value=0, value=0)
        f_exterior = st.number_input("Fotos de Exterior (Fachada):", min_value=0, value=0)
        f_equipo = st.number_input("Fotos de Equipo / Personal:", min_value=0, value=0)
        f_productos = st.number_input("Fotos de Productos / Servicios:", min_value=0, value=0)
        f_logo = st.number_input("Logotipo / Portada configurados (0 o 1):", min_value=0, max_value=1, value=0)

    st.markdown("### 4. Entradas Contextuales")
    desc_actual = st.text_area("Descripción Actual del Perfil (Si tiene):")
    servicios_actual = st.text_area("Servicios/Atributos Listados Actualmente:")
    resenas_actual = st.text_area("Reseñas Recientes (Para análisis semántico):", value="Cliente 1: Excelente servicio, el dentista fue muy paciente con mi tratamiento de ortodoncia.\nCliente 2: Buena atención pero tardaron un poco en atenderme a pesar de tener cita.")

    # --- BOTONES DE GENERACIÓN ---
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        generar_auditoria_btn = st.button("1. Generar Diagnóstico (Preventa)", use_container_width=True)
    with col_btn2:
        generar_entregables_btn = st.button("2. Generar Entregables (Posventa)", use_container_width=True)

# --- PANEL DE RESULTADOS DERECHO ---
with col_res:
    tab1, tab2 = st.tabs(["📊 1. Auditoría Comercial (Preventa)", "🛠️ 2. Entregables Técnicos (Posventa)"])
    
    # Recopilar variables
    fotos = {"interior": f_interior, "exterior": f_exterior, "equipo": f_equipo, "productos": f_productos, "logo_portada": f_logo}
    diagnostico = {
        "propiedad": propiedad_ficha, "nap": consistencia_nap, "pin": pin_ubicacion, "horarios": horarios_reales,
        "categoria": cat_optimizacion, "nombre": nombre_spam, "servicios": catalogo_servicios,
        "chat": chat_nativo, "contacto": contacto_rapido, "faqs": faqs_config,
        "calidad": calidad_visual, "frecuencia": frecuencia_resenas, "seo_respuestas": seo_respuestas, "crisis": gestion_crisis
    }

    # --- ACCIÓN GENERAR AUDITORÍA (PREVENTA) ---
    if generar_auditoria_btn:
        if not api_key_input:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        else:
            # Cálculo de variables locales
            metricas = calcular_metricas(diagnostico, fotos, busquedas_est, ticket_prom)
            st.session_state.datos_negocio = {
                "nombre": nombre_negocio,
                "giro": giro_comercial,
                "categoria_p": cat_principal,
                "categorias_s": cat_secundarias,
                "fotos": fotos,
                "metricas": metricas
            }
            
            # Silenciado de cualquier mención a "Gemini" o IA
            with st.spinner(""):
                try:
                    client = genai.Client(api_key=api_key_input)
                    prompt_diagnostico = "\n".join([f"- {k.title()}: {v}" for k, v in diagnostico.items()])
                    
                    prompt = f"""
Actúa como un Consultor de SEO Local Senior y Socio Director de la firma de posicionamiento 'LocalRank Consulting'.
Vas a redactar un informe de Diagnóstico de Visibilidad Comercial para el negocio '{nombre_negocio}' (Giro: {giro_comercial}) en el mercado mexicano.

REGLA DE NEGOCIO CRÍTICA: No entregues NINGÚN activo copiable listo de inmediato (no redactes descripciones completas, ni FAQs completas, ni plantillas de respuestas exactas). Esto es preventa. El cliente debe pagar para obtener las soluciones de implementación. Limítate a auditar, justificar y demostrar la pérdida económica por inacción.

DATOS DE ENTRADA:
- Nombre: {nombre_negocio}
- Categoría Principal: {cat_principal}
- Categorías Secundarias: {cat_secundarias}
- Descripción Actual: {desc_actual}

DIAGNÓSTICO BASE DE LA FICHA:
{prompt_diagnostico}

MÉTRICAS CLAVE GENERADAS POR NUESTRO SISTEMA:
- Score de Optimización Moz Local: {metricas['score']}/100 
- Fuga Financiera Mensual Calculada: ${metricas['fuga_mensual']:,} MXN mensuales.
- Plan Recomendado: {metricas['plan_recomendado']}

-----------------
CONSTRUYE EL INFORME DE PREVENTA CON LAS SIGUIENTES SECCIONES.
Usa los títulos idénticos marcados con 'Sección X:' para permitir la segmentación automática del PDF.

Sección 1: Resumen Ejecutivo y Diagnóstico Global
- Presenta el diagnóstico formal de nuestra firma.
- Expone el Score de Optimización de {metricas['score']}/100. Desglosa los pilares algorítmicos.
- Detalla los fallos críticos de visibilidad detectados y explica cómo afectan la confianza de los consumidores.

Sección 2: El Costo de la Inacción (Pérdida Financiera)
- Explica de forma comercial la ecuación de ingresos proyectada para Google Maps en México: IP = VP * TA * TC * VT.
- Demuestra que operar con un perfil desoptimizado causa una fuga de facturación mensual estimada de ${metricas['fuga_mensual']:,} MXN que está absorbiendo la competencia. Este bloque debe ser directo y de alto impacto persuasivo.

Sección 3: Auditoría y Gaps de Relevancia (Categorías)
- Valida la categoría principal '{cat_principal}' en base al giro comercial.
- Lista un mínimo de 5 subcategorías ideales recomendadas para este nicho.

Sección 4: Diagnóstico Visual e Inventario de Fotos
- Analiza las fotos declaradas. Explica el impacto psicológico y algorítmico de tener imágenes reales frente a fotos de stock.

Sección 5: Fugas Conversionales y Canales Activos
- Analiza las deficiencias detectadas en los canales activos de contacto (Chat, WhatsApp, FAQs abandonadas). Explica cuántos prospectos se pierden por no tener activos estos embudos.

Sección 6: Propuesta de Solución LocalRank Consulting
- Despliega formalmente la cotización de servicios profesionales de Alejandro Trejo:
  * Plan Básico - Fundamentos y SEO Local ($3,500 MXN)
  * Plan Avanzado - Implementación e Infraestructura ($6,500 MXN)
  * Plan Recurrente - Gestión y Blindaje Mensual ($4,500 MXN / mes)
- Argumenta firmemente por qué el '{metricas['plan_recomendado']}' es la solución inmediata ideal.

IMPORTANTE: Redacta en un tono impecable, dinámico, asertivo y directo en español. Evita redundancias de estilo como "es vital, ya que...".
"""
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.session_state.reporte_auditoria = response.text
                except Exception as e:
                    st.error(f"Error durante el procesamiento: {e}")

    # --- ACCIÓN GENERAR ENTREGABLES (POSVENTA) ---
    if generar_entregables_btn:
        if not api_key_input:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        else:
            metricas = calcular_metricas(diagnostico, fotos, busquedas_est, ticket_prom)
            st.session_state.datos_negocio = {
                "nombre": nombre_negocio,
                "giro": giro_comercial,
                "categoria_p": cat_principal,
                "categorias_s": cat_secundarias,
                "fotos": fotos,
                "metricas": metricas
            }
            
            with st.spinner(""):
                try:
                    client = genai.Client(api_key=api_key_input)
                    prompt = f"""
Actúa como un Consultor de SEO Local Senior de la firma 'LocalRank Consulting'.
Vas a redactar el Dossier Técnico de Entregables de Implementación para el negocio '{nombre_negocio}' (Giro: {giro_comercial}). Este es un documento puramente operativo que el cliente obtiene tras haber pagado.

Debes entregar las soluciones exactas optimizadas de forma directa, listas para que el cliente o tú las copien e implementen de inmediato en la ficha de Google Business Profile.

DATOS DE ENTRADA:
- Nombre: {nombre_negocio}
- Categoría Principal: {cat_principal}
- Categorías Secundarias: {cat_secundarias}

RESEÑAS DEL CLIENTE PARA ANÁLISIS SEMÁNTICO:
{resenas_actual}

-----------------
CONSTRUYE EL INFORME DE POSVENTA CON LAS SIGUIENTES SECCIONES.
Usa los títulos idénticos marcados con 'Sección X:' para permitir la segmentación automática del PDF.

Sección 1: Propuesta de Descripción de Alta Conversión
- Redacta una descripción comercial completamente nueva para Google Maps, con un límite estricto de 750 caracteres, lista para copiar y pegar de inmediato.
- Debe incluir la categoría principal y geolocalización natural de manera fluida en las primeras dos líneas (primeros 150 caracteres). Tono alineado al giro {giro_comercial}.

Sección 2: Plan Técnico de Fotos Prioritarias
- Detalla un listado accionable con 5 tomas fotográficas estratégicas que deben realizarse y subirse de forma inmediata al perfil de Google Business Profile.

Sección 3: Enlaces de Conversión Activa y WhatsApp
- Genera la propuesta exacta para los botones de contacto rápido.
- Redacta el mensaje parametrizado ideal para el Enlace de WhatsApp del negocio que dispare la intención de compra.
- Detalla la guía operativa para activar el chat nativo de Google Business Profile.

Sección 4: Despliegue de Preguntas Frecuentes (FAQs) Nativas
- Redacta exactamente 3 Preguntas Frecuentes (FAQs) con sus respuestas ideales optimizadas para el nicho.

Sección 5: Módulo de Respuestas de Reseñas (10 Plantillas SEO)
- En base a las opiniones de clientes provistas, genera exactamente 10 respuestas modelo de alta calidad (5 positivas de 5 estrellas agradeciendo, 3 de crisis de 1 estrella, 2 de información neutral).

Sección 6: Script de Captación Automatizada de Opiniones
- Redacta el script de texto exacto para WhatsApp o Correo electrónico que el negocio debe enviar a sus clientes para incentivar el flujo de opiniones de 5 estrellas de manera orgánica.

Sección 7: Guía Técnica de Integración Conversacional y Citas
- Detalla la guía técnica de configuración de agenda automatizada (TidyCal o similar), incluyendo buffer de tiempo recomendado, flujos de recordatorio y de correo electrónico.

IMPORTANTE: Escribe directamente el código de las soluciones listas para ser aplicadas en español. Mantén el estilo corporativo y directo de la firma.
"""
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.session_state.reporte_entregables = response.text
                except Exception as e:
                    st.error(f"Error durante el procesamiento: {e}")

    # --- RENDERIZADO DE LA PESTAÑA 1 (AUDITORÍA PREVENTA) ---
    with tab1:
        # Se elimina el condicional de aviso estático. El editor carga directamente el estado de sesión actual.
        editor_auditoria = st.text_area(
            "Editor de Auditoría (Preventa):",
            value=st.session_state.reporte_auditoria,
            height=500,
            key="area_auditoria"
        )
        # Sincronizar el valor editado por el usuario
        st.session_state.reporte_auditoria = editor_auditoria
        
        if st.session_state.reporte_auditoria:
            pdf_data = generar_pdf_bytes(st.session_state.reporte_auditoria, st.session_state.datos_negocio, "auditoria")
            st.download_button(
                label="Descargar PDF de Preventa",
                data=pdf_data,
                file_name=f"Auditoria_Preventa_LocalRank_{nombre_negocio.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # --- RENDERIZADO DE LA PESTAÑA 2 (ENTREGABLES POSVENTA) ---
    with tab2:
        editor_entregables = st.text_area(
            "Editor de Entregables (Posventa):",
            value=st.session_state.reporte_entregables,
            height=500,
            key="area_entregables"
        )
        st.session_state.reporte_entregables = editor_entregables
        
        if st.session_state.reporte_entregables:
            pdf_data_post = generar_pdf_bytes(st.session_state.reporte_entregables, st.session_state.datos_negocio, "entregables")
            st.download_button(
                label="Descargar PDF de Posventa",
                data=pdf_data_post,
                file_name=f"Entregables_Posventa_LocalRank_{nombre_negocio.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
