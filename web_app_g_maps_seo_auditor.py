import os
import io
import datetime
import streamlit as st

# Intentar importar la nueva librería de Gemini de Google de forma segura
try:
    from google import genai
    USING_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai_legacy
        USING_NEW_SDK = False
    except ImportError:
        st.error("Por favor, instala la dependencia ejecutando: pip install google-genai reportlab streamlit")
        st.stop()

# Importaciones requeridas para construir PDFs profesionales en ReportLab sin usar el disco local
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

st.set_page_config(
    page_title="LocalRank Consulting | G-Maps Auditor",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para lograr un diseño oscuro premium, limpio y mobile-first
st.markdown("""
    <style>
    .main {
        background-color: #0B0B0F;
        color: #F3F4F6;
    }
    div[data-testid="stSidebar"] {
        background-color: #12121A;
        border-right: 1px solid #1F2937;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input {
        background-color: #1E1E2F !important;
        color: #F3F4F6 !important;
        border: 1px solid #1F2937 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "reporte_auditoria" not in st.session_state:
    st.session_state.reporte_auditoria = ""
if "reporte_entregables" not in st.session_state:
    st.session_state.reporte_entregables = ""
if "metricas" not in st.session_state:
    st.session_state.metricas = {}

with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/google-maps.png", width=70)
    st.title("LocalRank Consulting")
    st.markdown("*Optimización de Google Maps CDMX 2026*")
    st.write("---")
    
    # Entrada de API Key con persistencia temporal
    api_input = st.text_input("Gemini API Key:", value=st.session_state.api_key, type="password")
    if api_input:
        st.session_state.api_key = api_input
        
    st.info("💡 Consejo para tu S23 Ultra: Guarda esta página en tus marcadores de pantalla de inicio para abrirla como una App nativa.")

st.title("🗺️ G-Maps Dual-Document Auditor")
st.subheader("Firma Especializada en Posicionamiento Local y Conversión")

# Columnas de entrada de datos adaptables (responsivas)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Identificación y Giro")
    nombre_negocio = st.text_input("Nombre o Enlace del Negocio:", "Dental Center Guadalajara")
    
    giro_comercial = st.selectbox(
        "Giro Comercial:",
        [
            "Salud (Clínicas, Consultorios, Hospitales)",
            "Gastronomía (Restaurantes, Cafeterías, Bares)",
            "Servicios Profesionales B2B (Corporativos, Despachos)",
            "Ocio, Turismo y Entretenimiento (Atracciones, Hoteles)"
        ]
    )
    
    cat_principal = st.text_input("Categoría Principal en Maps:", "Clínica dental")
    cat_secundarias = st.text_input("Subcategorías actuales (comas):", "Dentista, Ortodoncista, Implantes dentales")

with col2:
    st.subheader("2. Métricas de Mercado")
    volumen_busquedas = st.number_input("Búsquedas Mensuales Estimadas (Zona):", min_value=1, value=1500, step=100)
    ticket_promedio = st.number_input("Ticket Promedio del Establecimiento ($MXN):", min_value=1.0, value=1200.0, step=50.0)
    
    st.markdown("---")
    st.markdown("**Fórmulas de Cálculo de Captación Local CDMX 2026**")
    st.latex(r"I_P = V_P \times T_A \times T_C \times V_T")

st.subheader("3. Lista de Verificación de Diagnóstico Local")
tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs([
    "📂 B1: Fundamentos", "🏗️ B2: Arquitectura SEO", "💸 B3: Conversión", "⭐️ B4: Autoridad"
])

checklist_datos = {}

with tab_b1:
    checklist_datos["propiedad_ficha"] = st.radio("Propiedad de la Ficha:", ["Reclamada y Verificada", "Sin reclamar / Abandonada"], horizontal=True)
    checklist_datos["consistencia_nap"] = st.radio("Consistencia NAP (Web/Maps):", ["Consistente", "Datos distintos en Web/Ficha"], horizontal=True)
    checklist_datos["pin_ubicacion"] = st.radio("Pin de Ubicación:", ["Correcto (En la entrada)", "Desplazado / Incorrecto"], horizontal=True)
    checklist_datos["horarios_reales"] = st.radio("Horarios Reales y Festivos:", ["Actualizados", "Obsoletos / Sin festivos"], horizontal=True)

with tab_b2:
    checklist_datos["cat_optimizacion"] = st.radio("Categoría Principal/Secundarias:", ["Correctas y específicas", "Muy genéricas / Erróneas / Faltantes"])
    checklist_datos["nombre_spam"] = st.radio("Nombre Comercial Limpio:", ["Limpio y legal (Sin Spam)", "Spam / Keyword stuffing"])
    checklist_datos["catalogo_servicios"] = st.radio("Catálogo de Servicios:", ["Completo y redactado", "Vacío / Solo títulos sin descripción"])

with tab_b3:
    checklist_datos["chat_nativo"] = st.radio("Botón de Chat Nativo:", ["Activado y ágil", "Desactivado / Abandonado"])
    checklist_datos["contacto_rapido"] = st.radio("Enlace de Contacto Rápido:", ["Enlace optimizado", "Link roto / No tiene"])
    checklist_datos["faqs_config"] = st.radio("Preguntas Frecuentes (FAQs):", ["Configuradas (3-5 FAQs)", "Vacío / Abandonado"])

with tab_b4:
    checklist_datos["calidad_visual"] = st.radio("Calidad Visual Reciente:", ["Actualizadas y profesionales", "Fotos viejas / De stock"])
    checklist_datos["frecuencia_resenas"] = st.radio("Frecuencia de Reseñas:", ["Flujo constante activo", "Sin reseñas recientes / Estancado"])
    checklist_datos["seo_respuestas"] = st.radio("SEO en Respuestas de Reseñas:", ["Respuestas con SEO local", "\"Gracias\" plano / Sin responder"])
    checklist_datos["gestion_crisis"] = st.radio("Gestión de Crisis (1 Estrella):", ["Gestión profesional y comercial", "Respuestas reactivas / Ignoradas"])

col_f1, col_f2 = st.columns([1, 1])

with col_f1:
    st.markdown("#### Inventario Cuantitativo de Fotos")
    foto_interior = st.number_input("Fotos de Interior:", min_value=0, value=5)
    foto_exterior = st.number_input("Fotos de Exterior:", min_value=0, value=2)
    foto_equipo = st.number_input("Fotos de Equipo/Personal:", min_value=0, value=0)
    foto_productos = st.number_input("Fotos de Productos/Servicios:", min_value=0, value=12)
    foto_logo = st.number_input("Logo y Portada (0 o 1):", min_value=0, max_value=1, value=1)
    
    total_fotos = {
        "interior": foto_interior,
        "exterior": foto_exterior,
        "equipo": foto_equipo,
        "productos": foto_productos,
        "logo_portada": foto_logo
    }

with col_f2:
    st.markdown("#### Textos Existentes del Perfil")
    desc_actual = st.text_area("Descripción actual del perfil (dejar vacío si no tiene):", "")
    servicios_actual = st.text_area("Servicios/Atributos listados actualmente:", "")
    resenas_actual = st.text_area("Opiniones Recientes para Análisis Semántico:", "Cliente 1: Excelente servicio, el dentista fue muy paciente con mi tratamiento de ortodoncia.\nCliente 2: Buena atención pero tardaron un poco en atenderme a pesar de tener cita.")

def calcular_metricas_locales():
    score_gbp = 0
    if checklist_datos["propiedad_ficha"] == "Reclamada y Verificada": score_gbp += 8
    if checklist_datos["pin_ubicacion"] == "Correcto (En la entrada)": score_gbp += 8
    if checklist_datos["horarios_reales"] == "Actualizados": score_gbp += 6
    if checklist_datos["cat_optimizacion"] == "Correctas y específicas": score_gbp += 8
    if checklist_datos["nombre_spam"] == "Limpio y legal (Sin Spam)": score_gbp += 6
    
    score_onpage = 0
    if checklist_datos["consistencia_nap"] == "Consistente": score_onpage += 16
    
    score_resenas = 0
    if checklist_datos["frecuencia_resenas"] == "Flujo constante activo": score_resenas += 5
    if checklist_datos["seo_respuestas"] == "Respuestas con SEO local": score_resenas += 5
    if checklist_datos["gestion_crisis"] == "Gestión profesional y comercial": score_resenas += 5
    
    score_comportamiento = 0
    if checklist_datos["chat_nativo"] == "Activado y ágil": score_comportamiento += 2
    if checklist_datos["contacto_rapido"] == "Enlace optimizado": score_comportamiento += 3
    if checklist_datos["faqs_config"] == "Configuradas (3-5 FAQs)": score_comportamiento += 2
    
    score_fotos = 0
    tf = sum(total_fotos.values())
    if tf >= 50: score_fotos += 13
    elif tf >= 20: score_fotos += 8
    else: score_fotos += 3
    
    score_total = score_gbp + score_onpage + score_resenas + score_comportamiento + score_fotos
    
    tc = 0.30 # Tasa de conversión transaccional local 30%
    ingresos_optimo = volumen_busquedas * 0.06 * tc * ticket_promedio
    ingresos_actuales = volumen_busquedas * 0.015 * tc * ticket_promedio
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

def ejecutar_consulta_ia(tipo):
    if not st.session_state.api_key:
        st.error("Por favor, ingresa tu Gemini API Key en el panel lateral.")
        return

    st.session_state.metricas = calcular_metricas_locales()
    metricas = st.session_state.metricas
    
    prompt_diagnostico = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in checklist_datos.items()])

    if tipo == "auditoria":
        prompt = f"""
Actúa como un Consultor de SEO Local Senior y Socio Director de la firma 'LocalRank Consulting'.
Redacta un informe de Diagnóstico de Visibilidad Comercial para el negocio '{nombre_negocio}' (Giro: {giro_comercial}).

REGLA DE NEGOCIO: No entregues NINGÚN activo copiable de inmediato (no redactes descripciones completas, ni FAQs completas, ni respuestas exactas). Esto es preventa. El cliente debe pagar para obtener las soluciones exactas. Limítate a auditar, justificar y demostrar la pérdida económica por inacción.

DATOS:
- Nombre: {nombre_negocio}
- Categoría Principal: {cat_principal}
- Categorías Secundarias: {cat_secundarias}
- Descripción Actual: {desc_actual}
- Servicios Actuales: {servicios_actual}

MÉTRICAS CLAVE GENERADAS POR LA APP:
- Score de Optimización Moz Local: {metricas['score']}/100 
  (Breakdown: GBP {metricas['score_gbp']}%, Web On-Page {metricas['score_onpage']}%, Reseñas {metricas['score_resenas']}%, Comportamiento {metricas['score_behavior']}%, Fotos {metricas['score_photos']}%)
- Costo de la Inacción Financiera Calculado:
  * Ingreso Máximo Potencial (6.0% CTR): ${metricas['ingresos_optimo']:,} MXN.
  * Ingreso Actual Capturado (1.5% CTR): ${metricas['ingresos_actuales']:,} MXN.
  * FUGA DE DINERO MENSUAL: ${metricas['fuga_mensual']:,} MXN.
- Plan Comercial Recomendado por Score: {metricas['plan_recomendado']}

ESTADO DE CHECKLIST:
{prompt_diagnostico}

-----------------
CONSTRUYE EL INFORME DE PREVENTA CON LAS SIGUIENTES SECCIONES.
Usa los títulos idénticos marcados con 'Sección X:' para permitir la segmentación automática del PDF.

Sección 1: Resumen Ejecutivo y Diagnóstico Global
- Presenta el diagnóstico formal de la firma LocalRank Consulting.
- Expone de forma profesional el Score de Optimización de {metricas['score']}/100. Desglosa los pilares.

Sección 2: El Costo de la Inacción (Pérdida Financiera)
- Explica de forma comercial la ecuación de ingresos para Google Maps en México: IP = VP * TA * TC * VT.
- Demuestra que operar con un perfil desoptimizado causa una fuga mensual de ${metricas['fuga_mensual']:,} MXN.

Sección 3: Auditoría y Gaps de Relevancia (Categorías)
- Valida la categoría principal '{cat_principal}'. Lista 5 subcategorías ideales para este nicho.

Sección 4: Diagnóstico Visual e Inventario de Fotos
- Analiza las fotos declaradas. Explica el beneficio de tener imágenes reales frente a fotos de stock.

Sección 5: Fugas Conversionales y Canales de Tráfico
- Analiza las deficiencias detectadas en los canales activos de contacto (Chat, WhatsApp, FAQs abandonadas).

Sección 6: Propuesta de Solución LocalRank Consulting
- Despliega formalmente la cotización de servicios de Alejandro Trejo.
- Presenta de forma atractiva los planes y argumenta firmemente por qué el '{metricas['plan_recomendado']}' es el ideal.
"""
    else:
        prompt = f"""
Actúa como un Consultor de SEO Local Senior de 'LocalRank Consulting'.
Redacta el Dossier Técnico de Entregables de Implementación para el negocio '{nombre_negocio}' (Giro: {giro_comercial}). Este es un documento puramente operativo posventa.

Debes entregar las soluciones exactas optimizadas de forma directa, listas para copiar e implementar en la ficha.

DATOS:
- Nombre: {nombre_negocio}
- Categoría Principal: {cat_principal}
- Categorías Secundarias: {cat_secundarias}
- Opiniones de clientes: {resenas_actual}

-----------------
CONSTRUYE EL INFORME DE POSVENTA CON LAS SIGUIENTES SECCIONES.
Usa los títulos idénticos marcados con 'Sección X:' para permitir la segmentación automática del PDF.

Sección 1: Propuesta de Descripción de Alta Conversión
- Redacta una descripción comercial nueva de hasta 750 caracteres, con categoría principal e indicaciones locales fluidas en los primeros 150 caracteres.

Sección 2: Plan Técnico de Fotos Prioritarias
- Detalla 5 tomas fotográficas estratégicas que deben realizarse y subirse de inmediato.

Sección 3: Enlaces de Conversión Activa y WhatsApp
- Genera el mensaje parametrizado ideal para el enlace de WhatsApp que dispare la intención de compra.

Sección 4: Despliegue de Preguntas Frecuentes (FAQs) Nativas
- Redacta exactamente 3 FAQs optimizadas con palabras clave secundarias, listas para ser cargadas.

Sección 5: Módulo de Respuestas de Reseñas (10 Plantillas SEO)
- Genera exactamente 10 respuestas modelo hiper-optimizadas con SEO local (5 positivas de 5 estrellas, 3 de contención de crisis de 1 estrella, 2 de información neutral).

Sección 6: Script de Captación Automatizada de Opiniones
- Script de texto exacto para WhatsApp o Correo para incentivar el flujo recurrente de opiniones de 5 estrellas.

Sección 7: Guía Técnica de Integración Conversacional y Citas
- Detalla la guía técnica de configuración de agenda automatizada (TidyCal o similar), buffers y recordatorios.
"""

    with st.spinner("Procesando con Gemini AI..."):
        try:
            if USING_NEW_SDK:
                client = genai.Client(api_key=st.session_state.api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                resultado = response.text
            else:
                genai_legacy.configure(api_key=st.session_state.api_key)
                model = genai_legacy.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                resultado = response.text
                
            if tipo == "auditoria":
                st.session_state.reporte_auditoria = resultado
            else:
                st.session_state.reporte_entregables = resultado
            st.success("¡Contenido de la IA generado exitosamente!")
        except Exception as e:
            st.error(f"Error al contactar con la IA: {e}")

def generar_pdf_bytes(texto_contenido, tipo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=50,
        bottomMargin=50
    )
    
    # Colores corporativos según tipo de documento
    if tipo == "auditoria":
        primary_color = colors.HexColor("#1E3A8A")   # Azul marino elegante
        secondary_color = colors.HexColor("#DC2626") # Rojo de advertencia/pérdida
    else:
        primary_color = colors.HexColor("#111827")   # Carbón elegante
        secondary_color = colors.HexColor("#059669") # Verde de solución
        
    text_dark = colors.HexColor("#1F2937")
    border_light = colors.HexColor("#E5E7EB")
    bg_panel = colors.HexColor("#F9FAFB")

    styles = getSampleStyleSheet()
    
    # Configuración de estilos tipográficos para PDF
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=5
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

    # --- PORTADA DE ALTA GAMA ---
    story.append(Spacer(1, 30))
    story.append(Paragraph("LOCALRANK CONSULTING", ParagraphStyle('PortLogo', fontName='Helvetica-Bold', fontSize=14, textColor=secondary_color, alignment=TA_CENTER, spaceAfter=20)))
    story.append(Spacer(1, 40))
    
    if tipo == "auditoria":
        doc_titulo = "PLAN DE OPTIMIZACIÓN ALGORÍTMICA Y CAPTACIÓN LOCAL"
        doc_subtitulo = "Auditoría de Visibilidad Comercial y Costo de la Inacción (Preventa)"
    else:
        doc_titulo = "PLAN DE IMPLEMENTACIÓN Y ENTREGABLES OPERATIVOS"
        doc_subtitulo = "Dossier de Activos Técnicos Listos para Integración Directa (Posventa)"

    story.append(Paragraph(doc_titulo, ParagraphStyle('PortTitle', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=primary_color, alignment=TA_CENTER, spaceAfter=10)))
    story.append(Paragraph(doc_subtitulo, ParagraphStyle('PortSub', fontName='Helvetica', fontSize=12, leading=15, textColor=colors.HexColor("#4B5563"), alignment=TA_CENTER)))
    story.append(Spacer(1, 80))
    
    # Metadatos del Negocio
    datos = st.session_state.get("metricas", {})
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    if tipo == "auditoria":
        tabla_portada_data = [
            [Paragraph("PREPARADO PARA:", meta_label_style), Paragraph(nombre_negocio, meta_val_style)],
            [Paragraph("GIRO COMERCIAL:", meta_label_style), Paragraph(giro_comercial, meta_val_style)],
            [Paragraph("SCORE LOCAL:", meta_label_style), Paragraph(f"<b>{datos.get('score', 0)}/100</b> (Calificación Moz)", meta_val_style)],
            [Paragraph("FUGA DE FACTURACIÓN:", meta_label_style), Paragraph(f"<b>${datos.get('fuga_mensual', 0):,} MXN</b> / mensuales", ParagraphStyle('RedMeta', parent=meta_val_style, textColor=colors.HexColor("#DC2626")))],
            [Paragraph("FIRMA CONSULTORA:", meta_label_style), Paragraph("LocalRank Consulting", meta_val_style)],
            [Paragraph("FECHA DE EMISIÓN:", meta_label_style), Paragraph(fecha_actual, meta_val_style)],
        ]
    else:
        tabla_portada_data = [
            [Paragraph("PREPARADO PARA:", meta_label_style), Paragraph(nombre_negocio, meta_val_style)],
            [Paragraph("GIRO COMERCIAL:", meta_label_style), Paragraph(giro_comercial, meta_val_style)],
            [Paragraph("ACCESO OPERATIVO:", meta_label_style), Paragraph("<b>Solución Desbloqueada (Fase de Implementación)</b>", ParagraphStyle('GreenMeta', parent=meta_val_style, textColor=colors.HexColor("#059669")))],
            [Paragraph("FIRMA CONSULTORA:", meta_label_style), Paragraph("LocalRank Consulting", meta_val_style)],
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

    # --- CUERPO DEL INFORME ---
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
            if linea_sana.startswith(selector) or (linea_sana.isupper() and len(linea_sana) < 45):
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
        canvas.drawString(45, 28, "LocalRank Consulting | Plan de Evolución Local CDMX 2026")
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 45, 28, f"Página {page_num}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

st.markdown("---")
st.subheader("🛠️ Panel de Ejecución y Gestión de Reportes")

col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    st.markdown("### Fase 1: Auditoría de Preventa")
    if st.button("Lanzar Análisis de Preventa 🚀", use_container_width=True):
        ejecutar_consulta_ia("auditoria")
        
    # Editor interactivo para preventa
    texto_editado_auditoria = st.text_area(
        "Edita el reporte de preventa aquí antes de exportarlo:",
        value=st.session_state.reporte_auditoria,
        height=350,
        key="editor_auditoria"
    )
    st.session_state.reporte_auditoria = texto_editado_auditoria
    
    if st.session_state.reporte_auditoria:
        pdf_preventa_bytes = generar_pdf_bytes(st.session_state.reporte_auditoria, "auditoria")
        st.download_button(
            label="Descargar PDF de Preventa 🔴",
            data=pdf_preventa_bytes,
            file_name=f"LocalRank_Preventa_{nombre_negocio.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with col_btn2:
    st.markdown("### Fase 2: Entregables de Posventa")
    if st.button("Lanzar Generación de Activos 🟢", use_container_width=True):
        ejecutar_consulta_ia("entregables")
        
    # Editor interactivo para posventa
    texto_editado_entregables = st.text_area(
        "Edita el dossier de posventa aquí antes de exportarlo:",
        value=st.session_state.reporte_entregables,
        height=350,
        key="editor_entregables"
    )
    st.session_state.reporte_entregables = texto_editado_entregables
    
    if st.session_state.reporte_entregables:
        pdf_posventa_bytes = generar_pdf_bytes(st.session_state.reporte_entregables, "entregables")
        st.download_button(
            label="Descargar PDF de Posventa 🟢",
            data=pdf_posventa_bytes,
            file_name=f"LocalRank_Entregables_{nombre_negocio.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )