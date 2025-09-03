"""
Dashboard CRM - HOUSE (Versão Original Restaurada)
Dashboard do Funil HOUSE com gráficos em barras verticais dos usuários
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
base_url = os.getenv("API_BASE_URL", "https://crm.rdstation.com")
token = os.getenv("API_TOKEN", "681cb285978e2f00145fb15d")

# -------- Funções --------
@st.cache_data(ttl=300)
def fetch_house_funnel_data(base_url: str, token: str, start_date: str, end_date: str):
    """Busca dados específicos do Funil - HOUSE"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deals"
        headers = {"accept": "application/json"}
        
        params = {
            "token": token,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 200,
            "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_house_funnel_stages(base_url: str, token: str):
    """Busca etapas específicas do Funil - HOUSE"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deal_stages"
        headers = {"accept": "application/json"}
        params = {
            "token": token,
            "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "deal_stages" in data:
                return data["deal_stages"]
            else:
                return data
        else:
            return None
            
    except Exception as e:
        return None

def process_comparative_funnel_data(deals_data):
    """Processa dados para criar gráfico comparativo por usuário"""
    try:
        if not deals_data or "deals" not in deals_data:
            return None
        
        deals = deals_data["deals"]
        
        # Buscar TODOS os usuários que existem na API (mesma lógica do app_refactored.py)
        all_users = set()
        for deal in deals:
            if "user" in deal and deal["user"]:
                user_info = deal["user"]
                if isinstance(user_info, dict) and "name" in user_info:
                    user_name = user_info["name"].strip()
                    if user_name:  # Só adicionar se não for vazio
                        all_users.add(user_name)
        
        target_users = sorted(list(all_users))
        
        # Estrutura para armazenar dados por usuário e etapa
        user_stage_data = {}
        
        # Inicializar contadores para cada usuário
        for user in target_users:
            user_stage_data[user] = {}
        
        # Processar cada deal
        for deal in deals:
            if "user" in deal and deal["user"]:
                user_info = deal["user"]
                if isinstance(user_info, dict) and "name" in user_info:
                    user_name = user_info["name"].strip()
                    
                    # Verificar se é um dos usuários encontrados
                    if user_name in target_users:
                        # Obter etapa do deal
                        deal_stage = deal.get("deal_stage", {})
                        stage_name = deal_stage.get("name", "Sem Etapa")
                        
                        # Inicializar contador se não existir
                        if stage_name not in user_stage_data[user_name]:
                            user_stage_data[user_name][stage_name] = 0
                        
                        # Incrementar contador
                        user_stage_data[user_name][stage_name] += 1
        
        # Converter para DataFrame
        funnel_data = []
        for user in target_users:
            total_user_deals = sum(user_stage_data[user].values())
            if total_user_deals > 0:  # Só incluir usuários com dados
                for stage, count in user_stage_data[user].items():
                    funnel_data.append({
                        "Usuário": user,
                        "Etapa": stage,
                        "Quantidade": count
                    })
        
        return pd.DataFrame(funnel_data)
        
    except Exception as e:
        return None

def create_funnel_chart(stages_data, deals_data):
    """Cria gráfico de funil com as etapas"""
    try:
        if not stages_data or not deals_data or "deals" not in deals_data:
            return None
        
        deals = deals_data["deals"]
        
        # Contar deals por etapa
        stage_counts = {}
        for deal in deals:
            deal_stage = deal.get("deal_stage", {})
            stage_name = deal_stage.get("name", "Sem Etapa")
            stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1
        
        # Criar dados para o gráfico de funil
        funnel_data = []
        stage_order = ["Leads", "MQL", "SQL", "Proposta", "Negociação", "Em Andamento"]
        
        for stage in stage_order:
            if stage in stage_counts:
                funnel_data.append({
                    "stage": stage,
                    "count": stage_counts[stage]
                })
        
        return pd.DataFrame(funnel_data)
        
    except Exception as e:
        return None

# -------- Interface Principal --------
def main():
    st.title("🏠 Dashboard Funil - HOUSE")
    st.markdown("---")
    
    # Período padrão (últimos 30 dias)
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    
    # Buscar dados do Funil HOUSE
    house_data = fetch_house_funnel_data(
        base_url, 
        token, 
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    house_stages = fetch_house_funnel_stages(base_url, token)
    
    if house_data and house_stages:
            st.success(f"✅ Dados do Funil HOUSE carregados com sucesso!")
            
            # Criar abas para organizar o conteúdo
            tab1, tab2 = st.tabs(["📊 Funil HOUSE", "👥 Comparativo por Usuário"])
            
            with tab1:
                st.header("📊 Funil HOUSE - Visão Geral")
                
                # Gráfico de funil
                funnel_df = create_funnel_chart(house_stages, house_data)
                if funnel_df is not None and not funnel_df.empty:
                    st.subheader("🎯 Funil de Vendas - HOUSE")
                    
                    fig = go.Figure(go.Funnel(
                        y=funnel_df["stage"],
                        x=funnel_df["count"],
                        textinfo="value+percent initial"
                    ))
                    
                    fig.update_layout(
                        title="Funil de Vendas - HOUSE",
                        height=500,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Estatísticas do funil
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Deals", len(house_data.get("deals", [])))
                    with col2:
                        st.metric("Etapas Ativas", len(house_stages))
                    with col3:
                        if funnel_df is not None:
                            conversion_rate = ((funnel_df["count"].iloc[-1] / funnel_df["count"].iloc[0]) * 100) if len(funnel_df) > 1 else 0
                            st.metric("Taxa de Conversão", f"{conversion_rate:.1f}%")
                
                else:
                    st.info("📊 Dados insuficientes para criar gráfico de funil")
            
            with tab2:
                st.header("👥 Comparativo por Usuário")
                
                # Processar dados comparativos
                comparative_df = process_comparative_funnel_data(house_data)
                
                if comparative_df is not None and not comparative_df.empty:
                    st.subheader("📊 Comparativo de Negócios por Usuário")
                    
                    # Definir cores dinâmicas para cada usuário
                    color_palette = ["lightcoral", "lightblue", "lightgreen", "orange", "purple", "pink", "lightyellow", "lightcyan", "lightgray", "lightsteelblue"]
                    colors = {}
                    
                    for i, user in enumerate(comparative_df["Usuário"].unique()):
                        colors[user] = color_palette[i % len(color_palette)]
                    
                    # Gráfico de barras lado a lado
                    fig = go.Figure()
                    
                    for user in comparative_df["Usuário"].unique():
                        user_data = comparative_df[comparative_df["Usuário"] == user]
                        fig.add_trace(go.Bar(
                            x=user_data["Etapa"],
                            y=user_data["Quantidade"],
                            text=user_data["Quantidade"],
                            textposition='auto',
                            name=user,
                            marker_color=colors.get(user, "gray")
                        ))
                    
                    fig.update_layout(
                        title="Quantidade de Negócios por Etapa por Usuário",
                        xaxis_title="Etapas",
                        yaxis_title="Quantidade",
                        barmode='group',
                        height=500,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(size=12),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Opção para alternar entre gráficos
                    chart_type = st.radio(
                        "Tipo de Visualização:",
                        ["Barras Lado a Lado", "Barras Empilhadas"],
                        horizontal=True
                    )
                    
                    if chart_type == "Barras Empilhadas":
                        fig2 = go.Figure()
                        
                        for user in comparative_df["Usuário"].unique():
                            user_data = comparative_df[comparative_df["Usuário"] == user]
                            fig2.add_trace(go.Bar(
                                x=user_data["Etapa"],
                                y=user_data["Quantidade"],
                                text=user_data["Quantidade"],
                                textposition='auto',
                                name=user,
                                marker_color=colors.get(user, "gray")
                            ))
                        
                        fig2.update_layout(
                            title="Quantidade de Negócios por Etapa por Usuário (Empilhado)",
                            xaxis_title="Etapas",
                            yaxis_title="Quantidade",
                            barmode='stack',
                            height=500,
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Tabela de dados
                    st.subheader("📋 Dados Detalhados")
                    st.dataframe(comparative_df, use_container_width=True)
                    
                    # Download dos dados
                    csv = comparative_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Dados Comparativos",
                        data=csv,
                        file_name=f"house_comparativo_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.info("👥 Dados insuficientes para análise comparativa por usuário")
        
        else:
            st.error("❌ Erro ao carregar dados do Funil HOUSE")
            st.info("Verifique as configurações da API e tente novamente")
    
    # Informações sobre a API
    with st.expander("ℹ️ Configurações da API"):
        st.write(f"**Base URL:** {base_url}")
        st.write(f"**Token:** {token[:10]}...")
        st.write(f"**Período:** {start_date} a {end_date}")
        st.write("**Pipeline ID:** 689b59706e704a0024fc2374 (Funil - HOUSE)")

if __name__ == "__main__":
    main()