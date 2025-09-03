"""
Dashboard CRM - HOUSE (Versão Simplificada para Deploy)
Versão que funciona no Streamlit Cloud sem dependências externas
"""
import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

# -------- Configuração da Página --------
st.set_page_config(
    page_title="Dashboard Funil - HOUSE",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------- Configurações da API --------
# Usar variáveis de ambiente ou valores padrão
base_url = os.getenv("API_BASE_URL", "https://crm.rdstation.com")
token = os.getenv("API_TOKEN", "681cb285978e2f00145fb15d")

# -------- Funções --------
@st.cache_data(ttl=300)
def fetch_crm_data(base_url: str, token: str, start_date: str, end_date: str):
    """Busca dados do RD Station CRM"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deals"
        headers = {"accept": "application/json"}
        
        params = {
            "token": token,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 100
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

# -------- Interface Principal --------
def main():
    st.title("🏠 Dashboard Funil - HOUSE")
    st.markdown("---")
    
    # Filtros de data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Data Inicial",
            value=date.today() - timedelta(days=30),
            format="DD/MM/YYYY"
        )
    
    with col2:
        end_date = st.date_input(
            "Data Final", 
            value=date.today(),
            format="DD/MM/YYYY"
        )
    
    with col3:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    # Buscar dados
    if start_date and end_date:
        data = fetch_crm_data(
            base_url, 
            token, 
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if data:
            st.success(f"✅ Dados carregados com sucesso!")
            
            # Mostrar informações básicas
            if "deals" in data:
                deals = data["deals"]
                st.subheader(f"📊 Total de Deals: {len(deals)}")
                
                # Criar DataFrame
                if deals:
                    df = pd.DataFrame(deals)
                    st.dataframe(df.head(10))
                    
                    # Gráfico simples
                    if "stage" in df.columns:
                        stage_counts = df["stage"].value_counts()
                        fig = go.Figure(data=[go.Bar(x=stage_counts.index, y=stage_counts.values)])
                        fig.update_layout(title="Deals por Estágio", xaxis_title="Estágio", yaxis_title="Quantidade")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhum deal encontrado no período selecionado.")
            else:
                st.warning("Formato de dados inesperado da API.")
        else:
            st.error("❌ Erro ao carregar dados da API.")
            st.info("Verifique as configurações da API e tente novamente.")
    
    # Informações sobre a API
    with st.expander("ℹ️ Configurações da API"):
        st.write(f"**Base URL:** {base_url}")
        st.write(f"**Token:** {token[:10]}...")
        st.write(f"**Período:** {start_date} a {end_date}")

if __name__ == "__main__":
    main()