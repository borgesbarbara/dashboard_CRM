"""
Dashboard CRM - RD Station (Versão Refatorada)
Aplicação principal que utiliza a estrutura modular backend/frontend
"""
import os
import streamlit as st
from dotenv import load_dotenv

from frontend.pages.dashboard import render_dashboard_page

# Carregar variáveis de ambiente
load_dotenv()

# -------- Configuração de Auto-Refresh --------
# Configurar auto-refresh a cada 5 minutos (300 segundos)
st.set_page_config(
    page_title="Dashboard Funil - HOUSE",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Adicionar meta tag para auto-refresh
st.markdown(
    """
    <meta http-equiv="refresh" content="300">
    """,
    unsafe_allow_html=True
)

# Desabilitar menu e botão de deploy
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        .stApp > header {display: none;}
        .stApp > footer {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# -------- Configurações da API --------
# Configuração da API (valores padrão do .env)
base_url = os.getenv("API_BASE_URL", "https://crm.rdstation.com")
token = os.getenv("API_TOKEN", "681cb285978e2f00145fb15d")

# -------- Aplicação Principal --------
def main():
    """Função principal da aplicação"""
    try:
        # Renderizar página principal do dashboard
        render_dashboard_page()
        
        # (Removido) seção Sobre o Dashboard
        
    except Exception as e:
        st.error(f"❌ Erro na aplicação: {str(e)}")
        st.info("💡 Verifique se todas as dependências estão instaladas e a API está configurada corretamente.")


if __name__ == "__main__":
    main() 