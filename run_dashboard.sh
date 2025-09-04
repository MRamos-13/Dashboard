#!/bin/bash
# 🏥 DASHBOARD ESSALUD - Ejecutar Dashboard Python
# Dashboard interactivo con Streamlit

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏥 DASHBOARD ESSALUD - PYTHON/STREAMLIT${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}🐍 Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 encontrado${NC}"

# Verificar pip
echo -e "${YELLOW}📦 Verificando pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 no está instalado${NC}"
    echo -e "${CYAN}💡 Instala con: sudo apt install python3-pip${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 encontrado${NC}"

# Instalar dependencias
echo -e "${YELLOW}📚 Instalando dependencias...${NC}"
pip3 install -r requirements.txt --user
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Verificar archivo de datos
echo -e "${YELLOW}📄 Verificando datos...${NC}"
if [ ! -f "data.txt" ]; then
    echo -e "${RED}❌ Archivo data.txt no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Archivo data.txt encontrado${NC}"

# Ejecutar dashboard
echo -e "${YELLOW}🚀 Iniciando dashboard...${NC}"
echo -e "${BLUE}🌐 El dashboard se abrirá en: http://localhost:8501${NC}"
echo -e "${CYAN}💡 Presiona Ctrl+C para detener${NC}"
echo ""

streamlit run dashboard_essalud.py --server.headless true --server.port 8501 --server.address 0.0.0.0
