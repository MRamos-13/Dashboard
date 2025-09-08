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
                    network = parts[3].strip() if len(parts) > 3 else ""
                    study = parts[4].strip() if len(parts) > 4 else ""
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
        # Proyectos activos: En Ejecución + Enviado al Comité de Ética + Validación
        active_projects = len(df[df['status'].str.contains('Ejecucion|Ejecución|Enviado.*Comité|Validacion', case=False, na=False)])
        st.metric(
            label="🔄 Proyectos Activos",
            value=active_projects,
            delta=f"{active_projects/len(df)*100:.1f}% del total"
        )
    
    with col3:
        # Proyectos completados: Reporte de Resultado + Completo + IRRI completo
        completed_projects = len(df[df['status'].str.contains('Reporte.*Resultado|Completo|completo|IRRI.*completo', case=False, na=False)])
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
    # Obtener estados únicos reales de los datos
    unique_statuses = df['status'].unique()
    
    # Definir colores para diferentes tipos de estados
    def get_status_color(status):
        status_lower = status.lower()
        if 'elaboración' in status_lower or 'elaboracion' in status_lower:
            return '#FFE4B5'  # Naranja claro - En elaboración
        elif 'aprobado' in status_lower or 'comité' in status_lower:
            return '#98FB98'  # Verde claro - Aprobado
        elif 'ejecución' in status_lower or 'ejecucion' in status_lower:
            return '#90EE90'  # Verde - En ejecución
        elif 'completo' in status_lower or 'rri' in status_lower.lower():
            return '#87CEEB'  # Azul claro - Completado
        elif 'autorizacion' in status_lower or 'gerencia' in status_lower:
            return '#FFB6C1'  # Rosa claro - Pendiente autorización
        elif 'validacion' in status_lower:
            return '#DDA0DD'  # Ciruela claro - En validación
        elif 'espera' in status_lower or 'respuesta' in status_lower:
            return '#F0E68C'  # Amarillo claro - En espera
        elif 'manuscrito' in status_lower:
            return '#DDA0DD'  # Ciruela claro - Manuscrito
        else:
            return '#E6E6FA'  # Lavanda - Otros estados
    
    # Crear diccionario de colores basado en estados reales
    kanban_columns = {}
    for status in unique_statuses:
        kanban_columns[status] = get_status_color(status)
    
    # Agrupar proyectos por estado real
    status_groups = {}
    for status in unique_statuses:
        projects = df[df['status'] == status]
        if not projects.empty:
            status_groups[status] = projects
    
    return status_groups, kanban_columns

def create_kanban_display(status_groups, kanban_columns):
    """Crear la visualización del tablero Kanban con scroll mejorado"""
    st.markdown("### 📋 Tablero Kanban - Estados de Protocolos")
    
    # Crear HTML completo para el Kanban con scroll
    kanban_html = """
    <div style="
        overflow-x: auto;
        overflow-y: hidden;
        padding: 15px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <div style="
            display: flex;
            gap: 15px;
            min-width: max-content;
            padding-bottom: 10px;
        ">
    """
    
    # Generar columnas del Kanban
    for status, projects in status_groups.items():
        kanban_html += f"""
            <div style="
                min-width: 280px;
                max-width: 280px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                overflow: hidden;
            ">
                <!-- Header de la columna -->
                <div style="
                    background: {kanban_columns[status]};
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                    color: #333;
                    font-size: 14px;
                    border-bottom: 2px solid rgba(0,0,0,0.1);
                ">
                    <div style="font-size: 16px; margin-bottom: 5px;">{status}</div>
                    <div style="
                        background: rgba(255,255,255,0.3);
                        padding: 5px 10px;
                        border-radius: 20px;
                        display: inline-block;
                        font-size: 18px;
                        font-weight: bold;
                    ">{len(projects)} proyectos</div>
                </div>
                
                <!-- Contenedor de proyectos con scroll -->
                <div style="
                    max-height: 600px;
                    overflow-y: auto;
                    padding: 10px;
                    background: #fafafa;
                ">
        """
        
        # Generar tarjetas de proyectos
        for _, project in projects.iterrows():
            kanban_html += f"""
                    <div style="
                        background: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 10px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        transition: all 0.3s ease;
                        cursor: pointer;
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.05)'">
                        <div style="
                            font-weight: bold;
                            font-size: 13px;
                            color: #2c3e50;
                            margin-bottom: 8px;
                            line-height: 1.3;
                        ">{project['study'][:70]}{'...' if len(project['study']) > 70 else ''}</div>
                        
                        <div style="
                            font-size: 11px;
                            color: #7f8c8d;
                            margin-bottom: 4px;
                        ">👤 {project['manager'][:30]}{'...' if len(project['manager']) > 30 else ''}</div>
                        
                        <div style="
                            font-size: 11px;
                            color: #95a5a6;
                        ">🏥 {project['network'][:40]}{'...' if len(project['network']) > 40 else ''}</div>
                    </div>
            """
        
        kanban_html += """
                </div>
            </div>
        """
    
    kanban_html += """
        </div>
    </div>
    
    <style>
    /* Scrollbar personalizado */
    div[style*="overflow-y: auto"]::-webkit-scrollbar {
        width: 6px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Scrollbar horizontal */
    div[style*="overflow-x: auto"]::-webkit-scrollbar {
        height: 8px;
    }
    
    div[style*="overflow-x: auto"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    div[style*="overflow-x: auto"]::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    div[style*="overflow-x: auto"]::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """
    
    # Usar st.components.v1.html para renderizar el HTML correctamente
    import streamlit.components.v1 as components
    components.html(kanban_html, height=700, scrolling=True)

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.markdown('<h1 class="main-header">🏥 Dashboard - DIRECCIÓN DE INVESTIGACIÓN EN SALUD - IETSI</h1>', unsafe_allow_html=True)
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
    """.format(
        total_projects=len(df),
        priority_lines=df['priority_line'].nunique(),
        networks=df['network'].nunique(),
        statuses=df['status'].nunique()
    ))

if __name__ == "__main__":
    main()
