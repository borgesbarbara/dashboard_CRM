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

def clean_dataframe(df):
    """Limpa e prepara o DataFrame para exibição segura"""
    try:
        # Converter para string colunas problemáticas
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        
        # Remover colunas com dados muito complexos
        safe_columns = []
        for col in df.columns:
            try:
                # Testar se a coluna pode ser exibida
                test_df = df[[col]].head(1)
                st.dataframe(test_df, use_container_width=True)
                safe_columns.append(col)
            except:
                continue
        
        # Retornar apenas colunas seguras
        if safe_columns:
            return df[safe_columns]
        else:
            # Se nenhuma coluna for segura, criar uma versão básica
            return pd.DataFrame({
                'ID': range(len(df)),
                'Status': 'Dados carregados',
                'Total': len(df)
            })
            
    except Exception as e:
        # Fallback: DataFrame básico
        return pd.DataFrame({
            'ID': range(len(df)),
            'Status': 'Dados carregados',
            'Total': len(df)
        })

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
                    try:
                        df = pd.DataFrame(deals)
                        
                        # Limpar DataFrame para exibição segura
                        safe_df = clean_dataframe(df)
                        
                        # Exibir DataFrame limpo
                        st.subheader("📋 Dados dos Deals")
                        st.dataframe(safe_df, use_container_width=True)
                        
                        # Estatísticas básicas
                        st.subheader("📈 Estatísticas")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total de Deals", len(df))
                        
                        with col2:
                            if 'stage' in df.columns:
                                unique_stages = df['stage'].nunique()
                                st.metric("Estágios Únicos", unique_stages)
                            else:
                                st.metric("Colunas", len(df.columns))
                        
                        with col3:
                            if 'value' in df.columns:
                                try:
                                    total_value = df['value'].sum()
                                    st.metric("Valor Total", f"R$ {total_value:,.2f}")
                                except:
                                    st.metric("Colunas", len(df.columns))
                            else:
                                st.metric("Colunas", len(df.columns))
                        
                        # Gráfico simples (se possível)
                        if 'stage' in df.columns:
                            try:
                                stage_counts = df['stage'].value_counts()
                                if len(stage_counts) > 0:
                                    fig = go.Figure(data=[go.Bar(x=stage_counts.index, y=stage_counts.values)])
                                    fig.update_layout(
                                        title="Deals por Estágio", 
                                        xaxis_title="Estágio", 
                                        yaxis_title="Quantidade"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.info("📊 Gráfico não disponível para estes dados")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao processar dados: {str(e)}")
                        st.info("💡 Os dados foram carregados, mas há problemas na exibição")
                        
                        # Mostrar dados brutos como alternativa
                        st.subheader("📋 Dados Brutos (Primeiros 5)")
                        st.json(deals[:5])
                        
                else:
                    st.info("Nenhum deal encontrado no período selecionado.")
            else:
                st.warning("Formato de dados inesperado da API.")
                st.json(data)
        else:
            st.error("❌ Erro ao carregar dados da API.")
            st.info("Verifique as configurações da API e tente novamente.")
    
    # Informações sobre a API
    with st.expander("ℹ️ Configurações da API"):
        st.write(f"**Base URL:** {base_url}")
        st.write(f"**Token:** {token[:10]}...")
        if start_date and end_date:
            st.write(f"**Período:** {start_date} a {end_date}")

if __name__ == "__main__":
    main()