
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(
    page_title="IPL-CR | Índice de Paz Legislativa",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .indicator-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .paz-negativa {
        border-left: 5px solid #e74c3c;
        padding-left: 1rem;
    }
    .paz-positiva {
        border-left: 5px solid #27ae60;
        padding-left: 1rem;
    }
    .score-0 { color: #95a5a6; }
    .score-1 { color: #f39c12; }
    .score-2 { color: #27ae60; font-weight: bold; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
    .save-btn {
        background-color: #27ae60 !important;
        color: white !important;
    }
    .download-btn {
        background-color: #3498db !important;
        color: white !important;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []
if 'current_id' not in st.session_state:
    st.session_state.current_id = 1

# Diccionario de indicadores
INDICADORES_PN = {
    'PN1': {'nombre': 'Prevención de violencia', 'def': 'Busca prevenir o reducir violencia directa.', 'keywords': 'violencia, prevención del delito, homicidio'},
    'PN2': {'nombre': 'Reducción de criminalidad', 'def': 'Aborda delitos, criminalidad o inseguridad.', 'keywords': 'delincuencia, crimen organizado'},
    'PN3': {'nombre': 'Protección de víctimas', 'def': 'Protege o repara a víctimas.', 'keywords': 'víctimas, reparación, atención'},
    'PN4': {'nombre': 'Regulación del uso de la fuerza', 'def': 'Define límites, protocolos o controles de uso de fuerza.', 'keywords': 'fuerza pública, actuación policial'},
    'PN5': {'nombre': 'Armas / crimen organizado', 'def': 'Regula armas, narcotráfico o redes delictivas.', 'keywords': 'armas, narcotráfico, pandillas'},
    'PN6': {'nombre': 'Reforma penal', 'def': 'Modifica tipos penales, sanciones o proceso penal.', 'keywords': 'código penal, pena'},
    'PN7': {'nombre': 'Resolución alternativa de conflictos', 'def': 'Promueve mediación, conciliación o justicia restaurativa.', 'keywords': 'mediación, conciliación, RAC'},
    'PN8': {'nombre': 'Violencia doméstica/comunitaria', 'def': 'Aborda violencia intrafamiliar, de género o comunitaria.', 'keywords': 'violencia doméstica, acoso'},
    'PN9': {'nombre': 'Seguridad pública', 'def': 'Fortalece capacidades de seguridad pública.', 'keywords': 'seguridad ciudadana, policía'}
}

INDICADORES_PP = {
    'PP10': {'nombre': 'Acceso a justicia', 'def': 'Amplía acceso a justicia o tutela efectiva.', 'keywords': 'defensa pública, acceso a justicia'},
    'PP11': {'nombre': 'Transparencia / rendición de cuentas', 'def': 'Fortalece acceso a información y control público.', 'keywords': 'transparencia, datos abiertos'},
    'PP12': {'nombre': 'Reducción de corrupción', 'def': 'Crea controles anticorrupción o de probidad.', 'keywords': 'probidad, control interno'},
    'PP13': {'nombre': 'Derechos fundamentales', 'def': 'Amplía o protege derechos fundamentales.', 'keywords': 'derechos humanos, dignidad'},
    'PP14': {'nombre': 'Grupos vulnerables', 'def': 'Protege grupos vulnerables o históricamente excluidos.', 'keywords': 'niñez, mujeres, indígenas, discapacidad'},
    'PP15': {'nombre': 'Igualdad / no discriminación', 'def': 'Reduce discriminación o fortalece igualdad.', 'keywords': 'igualdad, equidad, inclusión'},
    'PP16': {'nombre': 'Educación', 'def': 'Fortalece educación pública o cultura de paz.', 'keywords': 'educación pública, cultura de paz'},
    'PP17': {'nombre': 'Salud / bienestar', 'def': 'Mejora salud pública o bienestar social.', 'keywords': 'CCSS, salud pública'},
    'PP18': {'nombre': 'Pobreza / desigualdad', 'def': 'Busca reducir pobreza o desigualdad.', 'keywords': 'pobreza, exclusión social'},
    'PP19': {'nombre': 'Participación ciudadana', 'def': 'Amplía participación, consulta o control ciudadano.', 'keywords': 'consulta pública, participación'},
    'PP20': {'nombre': 'Fortalecimiento institucional', 'def': 'Mejora gobernanza o coordinación institucional.', 'keywords': 'gobernanza, coordinación'},
    'PP21': {'nombre': 'Cohesión social', 'def': 'Fomenta convivencia, diálogo o reconciliación.', 'keywords': 'cohesión social, convivencia'},
    'PP22': {'nombre': 'Igualdad territorial', 'def': 'Reduce brechas territoriales o regionales.', 'keywords': 'zonas rurales, regionalización'},
    'PP23': {'nombre': 'Prevención estructural de violencia', 'def': 'Ataca causas estructurales de la violencia.', 'keywords': 'oportunidades, inclusión social'}
}

def calcular_totales(scores_pn, scores_pp):
    """Calcula totales y clasificación"""
    pn_total = sum(scores_pn.values())
    pp_total = sum(scores_pp.values())

    # Calcular porcentajes (máximos: PN=18, PP=28)
    pn_100 = round((pn_total / 18) * 100, 1)
    pp_100 = round((pp_total / 28) * 100, 1)

    # Clasificación
    if pn_100 >= 67 and pp_100 < 34:
        tipo = "Negativa"
    elif pp_100 >= 67 and pn_100 < 34:
        tipo = "Positiva"
    elif pn_100 >= 34 and pp_100 >= 34:
        tipo = "Mixta"
    else:
        tipo = "Baja incidencia"

    return pn_total, pp_total, pn_100, pp_100, tipo

def get_score_color(score):
    """Retorna clase CSS según puntaje"""
    if score == 0:
        return "score-0"
    elif score == 1:
        return "score-1"
    else:
        return "score-2"

def generar_excel(proyectos):
    """Genera el archivo Excel exacto al formato original"""
    if not proyectos:
        return None

    # Crear DataFrame
    df = pd.DataFrame(proyectos)

    # Reorganizar columnas para que coincidan con el formato original
    columnas_orden = [
        'ID', 'Año', 'Expediente', 'Título del proyecto', 'Fecha ingreso', 'Estado',
        'Tema principal', 'URL/Fuente'
    ] + list(INDICADORES_PN.keys()) + list(INDICADORES_PP.keys()) + [
        'PN_total', 'PP_total', 'PN_100', 'PP_100', 'Tipo_paz', 'Observaciones'
    ]

    df = df[columnas_orden]

    # Crear Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja principal
        df.to_excel(writer, sheet_name='Matriz_Leyes_CR', index=False)

        # Hoja de resumen
        resumen_data = {
            'Métrica': [
                'Total de proyectos registrados',
                'Promedio paz negativa',
                'Promedio paz positiva',
                'Proyectos tipo Negativa',
                'Proyectos tipo Positiva',
                'Proyectos tipo Mixta',
                'Proyectos tipo Baja incidencia'
            ],
            'Valor': [
                len(proyectos),
                round(df['PN_100'].mean(), 1) if len(proyectos) > 0 else 0,
                round(df['PP_100'].mean(), 1) if len(proyectos) > 0 else 0,
                len(df[df['Tipo_paz'] == 'Negativa']),
                len(df[df['Tipo_paz'] == 'Positiva']),
                len(df[df['Tipo_paz'] == 'Mixta']),
                len(df[df['Tipo_paz'] == 'Baja incidencia'])
            ]
        }
        pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen', index=False)

        # Distribución por año
        if len(proyectos) > 0:
            dist_año = df.groupby('Año').agg({
                'ID': 'count',
                'PN_100': 'mean',
                'PP_100': 'mean'
            }).reset_index()
            dist_año.columns = ['Año', 'N proyectos', 'Prom. PN', 'Prom. PP']
            dist_año.to_excel(writer, sheet_name='Resumen', startrow=10, index=False)

    output.seek(0)
    return output

# Sidebar - Navegación
st.sidebar.title("⚖️ IPL-CR")
st.sidebar.markdown("*Índice de Paz Legislativa*")
st.sidebar.markdown("*Costa Rica 2010-2024*")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navegación", [
    "📋 Nuevo Proyecto", 
    "📊 Ver Proyectos", 
    "📈 Dashboard", 
    "💾 Exportar Datos"
])

st.sidebar.markdown("---")
st.sidebar.info(f"Proyectos registrados: **{len(st.session_state.proyectos)}**")

# Página: Nuevo Proyecto
if page == "📋 Nuevo Proyecto":
    st.markdown('<div class="main-header">Codificación de Proyecto de Ley</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete la información del proyecto y asigne puntajes a los indicadores</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Información General")
        id_proyecto = st.number_input("ID", min_value=1, value=st.session_state.current_id)
        año = st.selectbox("Año", list(range(2010, 2025)))
        expediente = st.text_input("Número de Expediente", placeholder="Ej: 23.456")
        titulo = st.text_area("Título del Proyecto", placeholder="Ingrese el título completo...")
        fecha_ingreso = st.date_input("Fecha de Ingreso")
        estado = st.selectbox("Estado", ["Ingresado", "En trámite", "Aprobado", "Rechazado", "Archivado", "Retirado"])
        tema = st.text_input("Tema Principal", placeholder="Ej: Seguridad ciudadana, Educación...")
        url_fuente = st.text_input("URL/Fuente", placeholder="https://...")

    with col2:
        st.subheader("📝 Observaciones")
        observaciones = st.text_area("Notas metodológicas o contexto relevante", height=200)

        # Mostrar guía rápida
        with st.expander("📖 Ver guía de puntuación"):
            st.markdown("""
            **Escala de codificación:**
            - **0** = No aparece
            - **1** = Aparece indirectamente / Mención general
            - **2** = Aparece explícitamente con mecanismos concretos

            **Clasificación final:**
            - **Negativa**: Alta PN (≥67%), baja PP (<34%)
            - **Positiva**: Alta PP (≥67%), baja PN (<34%)
            - **Mixta**: Ambas medias/altas
            - **Baja incidencia**: Ambas bajas
            """)

    st.markdown("---")

    # Indicadores de Paz Negativa
    st.markdown('<div class="paz-negativa">', unsafe_allow_html=True)
    st.subheader("🔴 Indicadores de Paz Negativa (PN1-PN9)")
    st.markdown("*Reducción de violencia directa, coerción y victimización*")

    scores_pn = {}
    cols_pn = st.columns(3)
    for i, (codigo, info) in enumerate(INDICADORES_PN.items()):
        with cols_pn[i % 3]:
            with st.expander(f"**{codigo}**: {info['nombre']}"):
                st.caption(info['def'])
                st.caption(f"*Palabras clave: {info['keywords']}*")
                scores_pn[codigo] = st.radio(
                    f"Puntaje {codigo}",
                    options=[0, 1, 2],
                    format_func=lambda x: {0: "0 - No aparece", 1: "1 - Indirecto", 2: "2 - Explícito"}[x],
                    key=f"pn_{codigo}",
                    horizontal=True
                )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Indicadores de Paz Positiva
    st.markdown('<div class="paz-positiva">', unsafe_allow_html=True)
    st.subheader("🟢 Indicadores de Paz Positiva (PP10-PP23)")
    st.markdown("*Fortalecimiento de derechos, inclusión, equidad e instituciones*")

    scores_pp = {}
    cols_pp = st.columns(3)
    for i, (codigo, info) in enumerate(INDICADORES_PP.items()):
        with cols_pp[i % 3]:
            with st.expander(f"**{codigo}**: {info['nombre']}"):
                st.caption(info['def'])
                st.caption(f"*Palabras clave: {info['keywords']}*")
                scores_pp[codigo] = st.radio(
                    f"Puntaje {codigo}",
                    options=[0, 1, 2],
                    format_func=lambda x: {0: "0 - No aparece", 1: "1 - Indirecto", 2: "2 - Explícito"}[x],
                    key=f"pp_{codigo}",
                    horizontal=True
                )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Cálculo en tiempo real
    pn_total, pp_total, pn_100, pp_100, tipo = calcular_totales(scores_pn, scores_pp)

    col_res1, col_res2, col_res3, col_res4, col_res5 = st.columns(5)
    with col_res1:
        st.metric("PN Total", f"{pn_total}/18")
    with col_res2:
        st.metric("PP Total", f"{pp_total}/28")
    with col_res3:
        st.metric("PN %", f"{pn_100}%")
    with col_res4:
        st.metric("PP %", f"{pp_100}%")
    with col_res5:
        color_tipo = {"Negativa": "🔴", "Positiva": "🟢", "Mixta": "🟡", "Baja incidencia": "⚪"}[tipo]
        st.metric("Tipo de Paz", f"{color_tipo} {tipo}")

    # Botón guardar
    st.markdown("---")
    if st.button("💾 GUARDAR PROYECTO", type="primary", use_container_width=True):
        if not titulo:
            st.error("⚠️ El título del proyecto es obligatorio")
        else:
            proyecto = {
                'ID': id_proyecto,
                'Año': año,
                'Expediente': expediente,
                'Título del proyecto': titulo,
                'Fecha ingreso': fecha_ingreso.strftime("%Y-%m-%d"),
                'Estado': estado,
                'Tema principal': tema,
                'URL/Fuente': url_fuente,
                **scores_pn,
                **scores_pp,
                'PN_total': pn_total,
                'PP_total': pp_total,
                'PN_100': pn_100,
                'PP_100': pp_100,
                'Tipo_paz': tipo,
                'Observaciones': observaciones
            }

            # Verificar si ID ya existe y actualizar
            existing_idx = None
            for idx, p in enumerate(st.session_state.proyectos):
                if p['ID'] == id_proyecto:
                    existing_idx = idx
                    break

            if existing_idx is not None:
                st.session_state.proyectos[existing_idx] = proyecto
                st.success(f"✅ Proyecto #{id_proyecto} actualizado correctamente")
            else:
                st.session_state.proyectos.append(proyecto)
                st.session_state.current_id = max(p['ID'] for p in st.session_state.proyectos) + 1
                st.success(f"✅ Proyecto #{id_proyecto} guardado correctamente")

            st.balloons()

# Página: Ver Proyectos
elif page == "📊 Ver Proyectos":
    st.markdown('<div class="main-header">Proyectos Registrados</div>', unsafe_allow_html=True)

    if not st.session_state.proyectos:
        st.info("📭 No hay proyectos registrados. Vaya a 'Nuevo Proyecto' para comenzar.")
    else:
        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_año = st.multiselect("Filtrar por Año", sorted(set(p['Año'] for p in st.session_state.proyectos)))
        with col_f2:
            filtro_tipo = st.multiselect("Filtrar por Tipo de Paz", ["Negativa", "Positiva", "Mixta", "Baja incidencia"])
        with col_f3:
            filtro_tema = st.text_input("Buscar por tema o título")

        # Aplicar filtros
        proyectos_filtrados = st.session_state.proyectos
        if filtro_año:
            proyectos_filtrados = [p for p in proyectos_filtrados if p['Año'] in filtro_año]
        if filtro_tipo:
            proyectos_filtrados = [p for p in proyectos_filtrados if p['Tipo_paz'] in filtro_tipo]
        if filtro_tema:
            proyectos_filtrados = [p for p in proyectos_filtrados if filtro_tema.lower() in p['Título del proyecto'].lower() or filtro_tema.lower() in p['Tema principal'].lower()]

        st.markdown(f"**Mostrando {len(proyectos_filtrados)} de {len(st.session_state.proyectos)} proyectos**")

        # Tabla de proyectos
        df_display = pd.DataFrame(proyectos_filtrados)
        if not df_display.empty:
            df_display = df_display[['ID', 'Año', 'Expediente', 'Título del proyecto', 'Tema principal', 'PN_100', 'PP_100', 'Tipo_paz']]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Editar/Eliminar
        st.markdown("---")
        st.subheader("✏️ Editar o Eliminar Proyecto")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            id_editar = st.number_input("ID del proyecto a editar/eliminar", min_value=1, step=1)
        with col_e2:
            st.markdown("<br>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🗑️ Eliminar", type="secondary"):
                    st.session_state.proyectos = [p for p in st.session_state.proyectos if p['ID'] != id_editar]
                    st.success(f"Proyecto #{id_editar} eliminado")
                    st.rerun()
            with col_b2:
                if st.button("✏️ Cargar para editar"):
                    proyecto_edit = next((p for p in st.session_state.proyectos if p['ID'] == id_editar), None)
                    if proyecto_edit:
                        st.session_state.current_id = id_editar
                        st.info(f"Proyecto #{id_editar} cargado. Vaya a 'Nuevo Proyecto' para editar.")
                    else:
                        st.error("Proyecto no encontrado")

# Página: Dashboard
elif page == "📈 Dashboard":
    st.markdown('<div class="main-header">Dashboard de Análisis</div>', unsafe_allow_html=True)

    if not st.session_state.proyectos:
        st.info("📭 No hay datos para analizar. Registre proyectos primero.")
    else:
        df = pd.DataFrame(st.session_state.proyectos)

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Proyectos", len(df))
        with col2:
            st.metric("Promedio PN", f"{df['PN_100'].mean():.1f}%")
        with col3:
            st.metric("Promedio PP", f"{df['PP_100'].mean():.1f}%")
        with col4:
            tipo_mas_comun = df['Tipo_paz'].mode().iloc[0] if not df.empty else "N/A"
            st.metric("Tipo más común", tipo_mas_comun)

        st.markdown("---")

        # Gráficos
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Distribución por Tipo de Paz")
            tipo_counts = df['Tipo_paz'].value_counts()
            st.bar_chart(tipo_counts)

        with col_chart2:
            st.subheader("Evolución por Año")
            evolucion = df.groupby('Año').size()
            st.line_chart(evolucion)

        st.markdown("---")

        # Análisis por indicador
        st.subheader("Promedios por Indicador")

        col_ind1, col_ind2 = st.columns(2)

        with col_ind1:
            st.markdown("**Paz Negativa**")
            pn_data = {k: df[k].mean() for k in INDICADORES_PN.keys()}
            st.bar_chart(pd.Series(pn_data))

        with col_ind2:
            st.markdown("**Paz Positiva**")
            pp_data = {k: df[k].mean() for k in INDICADORES_PP.keys()}
            st.bar_chart(pd.Series(pp_data))

        st.markdown("---")

        # Scatter plot PN vs PP
        st.subheader("Relación Paz Negativa vs Paz Positiva")
        scatter_data = df[['PN_100', 'PP_100', 'Tipo_paz', 'Título del proyecto']]
        st.scatter_chart(scatter_data.set_index('Tipo_paz')[['PN_100', 'PP_100']])

# Página: Exportar
elif page == "💾 Exportar Datos":
    st.markdown('<div class="main-header">Exportar Base de Datos</div>', unsafe_allow_html=True)

    if not st.session_state.proyectos:
        st.info("📭 No hay proyectos para exportar.")
    else:
        st.markdown("""
        ### 📥 Descargar Excel

        El archivo generado incluirá:
        - **Hoja 'Matriz_Leyes_CR'**: Todos los proyectos codificados con los 23 indicadores
        - **Hoja 'Resumen'**: Estadísticas generales y distribución por año
        - **Formato idéntico** al template original para compatibilidad
        """)

        excel_file = generar_excel(st.session_state.proyectos)

        st.download_button(
            label="📥 DESCARGAR EXCEL (.xlsx)",
            data=excel_file,
            file_name=f"IPL_CR_Proyectos_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")

        # También exportar como JSON para backup
        st.markdown("### 💾 Backup JSON")
        json_str = json.dumps(st.session_state.proyectos, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 DESCARGAR BACKUP (.json)",
            data=json_str,
            file_name=f"IPL_CR_Backup_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

        st.markdown("---")

        # Importar datos
        st.markdown("### 📤 Importar Datos (JSON)")
        uploaded_file = st.file_uploader("Cargar archivo de backup", type=['json'])
        if uploaded_file is not None:
            try:
                data_import = json.load(uploaded_file)
                st.session_state.proyectos = data_import
                st.success(f"✅ {len(data_import)} proyectos importados correctamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error al importar: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    <strong>IPL-CR | Índice de Paz Legislativa de Costa Rica</strong><br>
    Basado en el marco teórico de Johan Galtung y Positive Peace (IEP)<br>
    2010-2024
</div>
""", unsafe_allow_html=True)
