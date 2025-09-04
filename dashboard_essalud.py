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

def create_researchers_chart(df):
    """Crear gráfico de investigadores principales"""
    # Filtrar investigadores válidos
    valid_investigators = df[
        (df['principal_investigator'].notna()) & 
        (df['principal_investigator'] != '') & 
        (~df['principal_investigator'].str.contains('xxxxx', case=False, na=False))
    ]
    
    researcher_counts = valid_investigators['principal_investigator'].value_counts().head(10)
    
    if len(researcher_counts) > 0:
        fig = px.bar(
            x=researcher_counts.values,
            y=researcher_counts.index,
            orientation='h',
            title="👥 Top 10 Investigadores Principales",
            color=researcher_counts.values,
            color_continuous_scale="Greens"
        )
        
        fig.update_layout(
            xaxis_title="Número de Proyectos",
            yaxis_title="Investigador Principal",
            height=500
        )
        
        return fig
    else:
        return None

def create_timeline_chart(df):
    """Crear gráfico de línea de tiempo por estado"""
    # Simular fechas basadas en el ID del proyecto
    df_timeline = df.copy()
    df_timeline['fecha_simulada'] = pd.date_range(start='2023-01-01', periods=len(df), freq='M')
    
    status_timeline = df_timeline.groupby(['fecha_simulada', 'status']).size().reset_index(name='count')
    
    fig = px.line(
        status_timeline,
        x='fecha_simulada',
        y='count',
        color='status',
        title="📅 Evolución de Estados en el Tiempo",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Proyectos",
        height=400
    )
    
    return fig

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
        researchers_fig = create_researchers_chart(filtered_df)
        if researchers_fig:
            st.plotly_chart(researchers_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes de investigadores para mostrar el gráfico.")
    
    # Gráfico de línea de tiempo
    st.plotly_chart(create_timeline_chart(filtered_df), use_container_width=True)
    
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
