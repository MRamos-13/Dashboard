#!/usr/bin/env python3
"""
🏥 DASHBOARD ESSALUD - Investigación y Desarrollo
Dashboard interactivo con datos reales usando Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter
import base64
from io import StringIO

# Configuración de la página
st.set_page_config(
    page_title="🏥 Dashboard ESSALUD",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Cargar y procesar datos del archivo data.txt"""
    try:
        # Leer el archivo data.txt
        with open('data.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Procesar las líneas (saltar las primeras 2 que son headers)
        data = []
        for i, line in enumerate(lines[2:], start=3):
            if line.strip() and '|' in line:
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 9:
                    # Limpiar datos
                    priority_line = parts[1].strip() if len(parts) > 1 else ""
                    manager = parts[2].strip() if len(parts) > 2 else ""
                    study = parts[3].strip() if len(parts) > 3 else ""
                    network = parts[4].strip() if len(parts) > 4 else ""
                    status = parts[5].strip() if len(parts) > 5 else ""
                    data_support = parts[6].strip() if len(parts) > 6 else ""
                    principal_investigator = parts[7].strip() if len(parts) > 7 else ""
                    co_investigators = parts[8].strip() if len(parts) > 8 else ""
                    national_network = parts[9].strip() if len(parts) > 9 else ""
                    
                    # Filtrar líneas vacías o con datos incompletos
                    if priority_line and study and not priority_line.startswith('---'):
                        data.append({
                            'id': len(data) + 1,
                            'priority_line': priority_line,
                            'manager': manager,
                            'study': study,
                            'network': network,
                            'status': status,
                            'data_support': data_support,
                            'principal_investigator': principal_investigator,
                            'co_investigators': co_investigators,
                            'national_network': national_network
                        })
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

def create_metrics(df):
    """Crear métricas principales"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total de Proyectos",
            value=len(df),
            delta=f"+{len(df)} proyectos activos"
        )
    
    with col2:
        active_projects = len(df[df['status'].str.contains('Ejecucion|Ejecución', case=False, na=False)])
        st.metric(
            label="🔄 Proyectos Activos",
            value=active_projects,
            delta=f"{active_projects/len(df)*100:.1f}% del total"
        )
    
    with col3:
        completed_projects = len(df[df['status'].str.contains('Completo|completo', case=False, na=False)])
        st.metric(
            label="✅ Proyectos Completados",
            value=completed_projects,
            delta=f"{completed_projects/len(df)*100:.1f}% del total"
        )
    
    with col4:
        unique_lines = df['priority_line'].nunique()
        st.metric(
            label="🏥 Líneas Prioritarias",
            value=unique_lines,
            delta=f"{unique_lines} líneas temáticas"
        )

def create_priority_chart(df):
    """Crear gráfico de líneas prioritarias"""
    priority_counts = df['priority_line'].value_counts()
    
    fig = px.pie(
        values=priority_counts.values,
        names=priority_counts.index,
        title="📊 Distribución por Líneas Prioritarias",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
    )
    
    return fig

def create_status_chart(df):
    """Crear gráfico de estados"""
    status_counts = df['status'].value_counts()
    
    fig = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        title="📈 Estado de los Protocolos",
        color=status_counts.values,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        xaxis_title="Estado del Protocolo",
        yaxis_title="Número de Proyectos",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def create_network_chart(df):
    """Crear gráfico de redes prestacionales"""
    network_counts = df['network'].value_counts()
    
    fig = px.bar(
        x=network_counts.values,
        y=network_counts.index,
        orientation='h',
        title="🏥 Proyectos por Red Prestacional",
        color=network_counts.values,
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(
        xaxis_title="Número de Proyectos",
        yaxis_title="Red Prestacional",
        height=500
    )
    
    return fig

def create_managers_chart(df):
    """Crear gráfico de todos los gestores DIS con cantidad de estudios"""
    # Filtrar gestores válidos
    valid_managers = df[
        (df['manager'].notna()) & 
        (df['manager'] != '') & 
        (~df['manager'].str.contains('xxxxx', case=False, na=False))
    ]
    
    manager_counts = valid_managers['manager'].value_counts()
    
    if len(manager_counts) > 0:
        fig = px.bar(
            x=manager_counts.values,
            y=manager_counts.index,
            orientation='h',
            title="👥 Gestores DIS y Cantidad de Estudios",
            color=manager_counts.values,
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            xaxis_title="Número de Estudios",
            yaxis_title="Gestor DIS",
            height=500
        )
        
        return fig
    else:
        return None

def create_kanban_board(df):
    """Crear tablero Kanban basado en estados del protocolo"""
    # Definir columnas del Kanban basadas en los estados encontrados
    kanban_columns = {
        'Elaboración del protocolo': '#FFE4B5',  # Naranja claro
        'Elaboración de protocolo': '#FFE4B5',   # Naranja claro
        'Elaboracion de protocolo': '#FFE4B5',   # Naranja claro
        'Elaboracinn de protocolo': '#FFE4B5',   # Naranja claro
        'Elaboracionn de protocolo': '#FFE4B5',  # Naranja claro
        'Aprobado Comité de Etica': '#98FB98',   # Verde claro
        'En Ejecución': '#90EE90',               # Verde
        'En Ejecucion': '#90EE90',               # Verde
        'RRI 1 Completo': '#87CEEB',            # Azul claro
        'IRRI 1 (completo RR2 (en proyecto para III trimestre)': '#87CEEB',  # Azul claro
        'Para autorizacion por Gerencia General': '#FFB6C1',  # Rosa claro
        'Validacion de protocolo': '#DDA0DD',    # Ciruela claro
        'RRI 1': '#87CEEB',                     # Azul claro
        'En espera de respuesta de informe': '#F0E68C',  # Amarillo claro
        'Elaboración de manuscrito': '#DDA0DD'   # Ciruela claro
    }
    
    # Agrupar proyectos por estado
    status_groups = {}
    for status, color in kanban_columns.items():
        projects = df[df['status'].str.contains(status, case=False, na=False)]
        if not projects.empty:
            status_groups[status] = projects
    
    return status_groups, kanban_columns

def create_kanban_display(status_groups, kanban_columns):
    """Crear la visualización del tablero Kanban"""
    st.markdown("### 📋 Tablero Kanban - Estados de Protocolos")
    
    # Crear columnas para el Kanban
    cols = st.columns(len(status_groups))
    
    for i, (status, projects) in enumerate(status_groups.items()):
        with cols[i]:
            # Título de la columna con contador
            st.markdown(f"""
            <div style="
                background-color: {kanban_columns[status]};
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 10px;
                text-align: center;
                font-weight: bold;
                color: #333;
            ">
                {status}<br>
                <span style="font-size: 1.2em;">{len(projects)} proyectos</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar proyectos en esta columna
            for _, project in projects.iterrows():
                st.markdown(f"""
                <div style="
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <strong>{project['study'][:50]}{'...' if len(project['study']) > 50 else ''}</strong><br>
                    <small style="color: #666;">
                        👤 {project['manager']}<br>
                        🏥 {project['network'][:30]}{'...' if len(project['network']) > 30 else ''}
                    </small>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.markdown('<h1 class="main-header">🏥 Dashboard ESSALUD - Investigación y Desarrollo</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de Gestión de Proyectos de Investigación")
    
    # Botón de actualización simple
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**📊 Dashboard ESSALUD - Investigación y Desarrollo**")
    
    with col2:
        if st.button("🔄 Actualizar", help="Actualiza los datos del dashboard"):
            st.rerun()
    
    # Cargar datos
    df = load_data()
    
    if df.empty:
        st.error("No se pudieron cargar los datos. Verifica que el archivo data.txt esté presente.")
        return
    
    # Sidebar con filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por línea prioritaria
    priority_lines = ['Todas'] + sorted(df['priority_line'].unique().tolist())
    selected_priority = st.sidebar.selectbox("Línea Prioritaria", priority_lines)
    
    # Filtro por estado
    statuses = ['Todos'] + sorted(df['status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Estado del Protocolo", statuses)
    
    # Filtro por red prestacional
    networks = ['Todas'] + sorted(df['network'].unique().tolist())
    selected_network = st.sidebar.selectbox("Red Prestacional", networks)
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if selected_priority != 'Todas':
        filtered_df = filtered_df[filtered_df['priority_line'] == selected_priority]
    
    if selected_status != 'Todos':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    if selected_network != 'Todas':
        filtered_df = filtered_df[filtered_df['network'] == selected_network]
    
    # Métricas principales
    st.header("📊 Métricas Generales")
    create_metrics(filtered_df)
    
    st.markdown("---")
    
    # Tablero Kanban
    status_groups, kanban_columns = create_kanban_board(filtered_df)
    create_kanban_display(status_groups, kanban_columns)
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_priority_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_status_chart(filtered_df), use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.plotly_chart(create_network_chart(filtered_df), use_container_width=True)
    
    with col4:
        managers_fig = create_managers_chart(filtered_df)
        if managers_fig:
            st.plotly_chart(managers_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes de gestores DIS para mostrar el gráfico.")
    
    st.markdown("---")
    
    # Tabla de proyectos
    st.header("�� Proyectos de Investigación")
    
    # Botón de descarga
    csv = filtered_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="proyectos_essalud.csv">📥 Descargar CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Mostrar tabla
    st.dataframe(
        filtered_df[['priority_line', 'study', 'network', 'status', 'principal_investigator', 'co_investigators']],
        use_container_width=True,
        height=400
    )
    
    # Información adicional
    st.markdown("---")
    st.markdown("### ℹ️ Información del Dashboard")
    st.info("""
    **Dashboard ESSALUD - Investigación y Desarrollo**
    
    - **Total de proyectos**: {total_projects}
    - **Líneas prioritarias**: {priority_lines}
    - **Redes prestacionales**: {networks}
    - **Estados de protocolos**: {statuses}
    
    Este dashboard muestra información en tiempo real sobre los proyectos de investigación 
    de ESSALUD, incluyendo líneas prioritarias, estados de protocolos, redes prestacionales 
    y investigadores principales.
    """.format(
        total_projects=len(df),
        priority_lines=df['priority_line'].nunique(),
        networks=df['network'].nunique(),
        statuses=df['status'].nunique()
    ))

if __name__ == "__main__":
    main()
