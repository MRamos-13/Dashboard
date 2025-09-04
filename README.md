# 🏥 Dashboard ESSALUD - Investigación y Desarrollo

Dashboard interactivo para la gestión de proyectos de investigación de ESSALUD, desarrollado con Streamlit y Plotly.

## 📊 Características

- **Gráficos Interactivos**: Visualizaciones dinámicas con Plotly
- **Filtros Dinámicos**: Filtrado por línea prioritaria, estado y red prestacional
- **Tabla Completa**: Vista detallada de todos los proyectos
- **Exportación**: Descarga de datos en formato CSV
- **Responsive**: Funciona en todos los dispositivos
- **Tiempo Real**: Actualización manual de datos

## 🚀 Despliegue en Streamlit Cloud

### Opción 1: Despliegue Directo

1. **Sube este repositorio a GitHub**
2. **Ve a [Streamlit Cloud](https://share.streamlit.io/)**
3. **Conecta tu cuenta de GitHub**
4. **Selecciona este repositorio**
5. **Configura el despliegue:**
   - **Main file path**: `dashboard_essalud.py`
   - **Python version**: 3.10
6. **Haz clic en "Deploy!"**

### Opción 2: Despliegue Local

```bash
# Clonar el repositorio
git clone <tu-repositorio-github>
cd DASHBOARD

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
streamlit run dashboard_essalud.py
```

## 📁 Estructura del Proyecto

```
DASHBOARD/
├── dashboard_essalud.py    # Aplicación principal de Streamlit
├── data.txt               # Datos de proyectos de investigación
├── requirements.txt       # Dependencias de Python
├── run_dashboard.sh       # Script de ejecución
├── README.md             # Documentación
└── .gitignore           # Archivos ignorados por Git
```

## 📋 Requisitos

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- Plotly 5.15.0+
- NumPy 1.24.0+

## 🔧 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
./run_dashboard.sh
```

## 📊 Datos

El dashboard procesa automáticamente el archivo `data.txt` que contiene información sobre:

- **Líneas Prioritarias**: Temas de investigación
- **Estudios**: Descripción de proyectos
- **Redes Prestacionales**: Ubicación de los proyectos
- **Estados**: Estado actual del protocolo
- **Investigadores**: Investigadores principales y co-investigadores

## 🎯 Uso

1. **Filtros**: Usa el sidebar para filtrar por línea prioritaria, estado o red
2. **Gráficos**: Interactúa con los gráficos para explorar los datos
3. **Tabla**: Revisa la tabla completa de proyectos
4. **Exportación**: Descarga los datos filtrados en CSV
5. **Actualización**: Usa el botón "Actualizar" para refrescar los datos

## 🌐 Acceso

- **Local**: http://localhost:8501
- **Streamlit Cloud**: https://tu-app.streamlit.app

## 📝 Notas

- El dashboard se actualiza automáticamente al modificar `data.txt`
- Los gráficos son completamente interactivos
- Los datos se procesan dinámicamente
- Compatible con dispositivos móviles

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

---

**Desarrollado para ESSALUD - Investigación y Desarrollo** 🏥