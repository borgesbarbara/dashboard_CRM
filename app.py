
import os
import json
from datetime import date, timedelta
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

# -------- Configuração de Auto-Refresh --------
# Configurar auto-refresh a cada 5 minutos (300 segundos)
st.set_page_config(
    page_title="Dashboard Funil - HOUSE",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar meta tag para auto-refresh
st.markdown(
    """
    <meta http-equiv="refresh" content="300">
    """,
    unsafe_allow_html=True
)

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

@st.cache_data(ttl=300)
def fetch_real_stages(base_url: str, token: str):
    """Busca as etapas reais dos funis de vendas"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deal_stages"
        headers = {"accept": "application/json"}
        params = {"token": token}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Retornar apenas a lista de etapas se existir
            if "deal_stages" in data:
                return data["deal_stages"]
            else:
                return data
        else:
            return None
            
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_pipeline_stages(base_url: str, token: str):
    """Busca funis e etapas do RD Station CRM"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deal_pipelines"
        
        # Tentar primeiro com Authorization header
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        
        # Se falhou, tentar com token como parâmetro (como funcionou antes)
        params = {"token": token}
        headers = {"accept": "application/json"}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_stage_details(base_url: str, token: str, stage_id: str):
    """Busca detalhes de uma etapa específica"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deal_stages/{stage_id}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        return None

def process_deals_data(deals_data, selected_team="Todos"):
    """Processa dados de negócios em formato de funil"""
    try:
        if not deals_data or "deals" not in deals_data:
            return None
        
        deals = deals_data["deals"]
        
        # Mapeamento de usuários para times
        team_mapping = {
            "Equipe Fenix": ["Paola Chagas"],
            "Equipe Bulls": ["Maria Eduarda "]  # Espaço extra no final
        }
        
        # Filtrar negócios por time se selecionado
        if selected_team != "Todos" and selected_team in team_mapping:
            team_users = team_mapping[selected_team]
            filtered_deals = []
            
            for deal in deals:
                if "user" in deal and deal["user"]:
                    user_info = deal["user"]
                    if isinstance(user_info, dict) and "name" in user_info:
                        user_name = user_info["name"]
                        # Comparação mais robusta (ignora espaços extras)
                        if any(user_name.strip() == team_user.strip() for team_user in team_users):
                            filtered_deals.append(deal)
            
            deals = filtered_deals
        
        # Criar dados de funil baseados no rating
        stage_counts = {}
        for deal in deals:
            rating = deal.get("rating", 0)
            if rating == 1:
                stage = "Leads"
            elif rating == 2:
                stage = "MQL"
            elif rating == 3:
                stage = "SQL"
            elif rating == 4:
                stage = "Proposta"
            elif rating == 5:
                stage = "Negociação"
            else:
                stage = "Em Andamento"
            
            if stage not in stage_counts:
                stage_counts[stage] = 0
            stage_counts[stage] += 1
        
        # Criar DataFrame para o gráfico
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

@st.cache_data(ttl=300)
def fetch_team_pipelines(base_url: str, token: str):
    """Busca funis específicos das equipes Bulls e Fenix"""
    try:
        url = f"{base_url.rstrip('/')}/api/v1/deal_pipelines"
        headers = {"accept": "application/json"}
        params = {"token": token}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            all_pipelines = response.json()
            
            # Filtrar apenas funis das equipes específicas
            team_pipelines = []
            for pipeline in all_pipelines:
                pipeline_name = pipeline.get('name', '').lower()
                if 'bulls' in pipeline_name or 'bull' in pipeline_name or 'fenix' in pipeline_name or 'fênix' in pipeline_name:
                    team_pipelines.append(pipeline)
            
            return team_pipelines
        else:
            return None
            
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_house_funnel_data(base_url: str, token: str, start_date: str, end_date: str):
    """Busca dados específicos do Funil - HOUSE"""
    try:
        # Buscar deals do funil específico
        url = f"{base_url.rstrip('/')}/api/v1/deals"
        headers = {"accept": "application/json"}
        
        params = {
            "token": token,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 100,
            "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
        }
        
        print(f"DEBUG: Buscando deals do HOUSE em: {url}")
        print(f"DEBUG: Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"DEBUG: Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Deals do HOUSE encontrados: {len(data.get('deals', []))}")
            return data
        else:
            print(f"DEBUG: Erro na requisição de deals - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_house_funnel_stages(base_url: str, token: str):
    """Busca etapas específicas do Funil - HOUSE"""
    try:
        # Usar o parâmetro deal_pipeline_id para filtrar diretamente
        url = f"{base_url.rstrip('/')}/api/v1/deal_stages"
        headers = {"accept": "application/json"}
        params = {
            "token": token,
            "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
        }
        
        print(f"DEBUG: Buscando etapas do HOUSE em: {url}")
        print(f"DEBUG: Headers: {headers}")
        print(f"DEBUG: Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Response Text (primeiros 200 chars): {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if "deal_stages" in data:
                stages = data["deal_stages"]
                print(f"DEBUG: Total de etapas do HOUSE encontradas: {len(stages)}")
                
                # Verificar se as etapas são realmente do HOUSE
                for i, stage in enumerate(stages):
                    pipeline_info = stage.get("deal_pipeline", {})
                    pipeline_id = pipeline_info.get("id")
                    pipeline_name = pipeline_info.get("name", "N/A")
                    print(f"DEBUG: Etapa {i+1}: {stage.get('name', 'N/A')} - Pipeline: {pipeline_name} (ID: {pipeline_id})")
                
                return stages
            else:
                print(f"DEBUG: 'deal_stages' não encontrado nos dados")
                return data
        else:
            print(f"DEBUG: Erro na requisição - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_house_stage_details(base_url: str, token: str, start_date: str, end_date: str):
    """Busca informações detalhadas de cada etapa do Funil - HOUSE"""
    try:
        # Primeiro, buscar as etapas do HOUSE
        stages_data = fetch_house_funnel_stages(base_url, token)
        if not stages_data:
            return None
            
        # Buscar deals do HOUSE
        deals_data = fetch_house_funnel_data(base_url, token, start_date, end_date)
        if not deals_data or "deals" not in deals_data:
            return None
            
        deals = deals_data["deals"]
        print(f"DEBUG: Total de deals do HOUSE: {len(deals)}")
        
        # Criar dicionário para armazenar dados de cada etapa
        stage_details = {}
        
        # Inicializar contadores para cada etapa
        for stage in stages_data:
            stage_id = stage["id"]
            stage_name = stage["name"]
            stage_order = stage["order"]
            
            stage_details[stage_id] = {
                "name": stage_name,
                "nickname": stage.get("nickname", ""),
                "order": stage_order,
                "id": stage_id,
                "deals_count": 0,
                "total_value": 0.0,
                "avg_value": 0.0,
                "deals": []
            }
        
        # Processar cada deal e distribuir pelas etapas
        for deal in deals:
            deal_stage_id = deal.get("deal_stage", {}).get("id")
            deal_value = deal.get("value", 0) or 0
            deal_user = deal.get("user", {}).get("name", "Sem usuário")
            
            print(f"DEBUG: Processando deal - Stage ID: {deal_stage_id}, User: {deal_user}, Value: {deal_value}")
            
            if deal_stage_id and deal_stage_id in stage_details:
                stage_details[deal_stage_id]["deals_count"] += 1
                stage_details[deal_stage_id]["total_value"] += deal_value
                stage_details[deal_stage_id]["deals"].append({
                    "id": deal.get("id"),
                    "name": deal.get("name", "Sem nome"),
                    "value": deal_value,
                    "user": deal_user,
                    "created_at": deal.get("created_at")
                })
            else:
                print(f"DEBUG: Deal ignorado - Stage ID não encontrado: {deal_stage_id}")
        
        # Debug: Mostrar distribuição de usuários
        user_distribution = {}
        for stage_id, stage_data in stage_details.items():
            for deal in stage_data["deals"]:
                user = deal["user"]
                if user not in user_distribution:
                    user_distribution[user] = 0
                user_distribution[user] += 1
        
        print(f"DEBUG: Distribuição de usuários: {user_distribution}")
        
        # Calcular valores médios
        for stage_id, stage_data in stage_details.items():
            if stage_data["deals_count"] > 0:
                stage_data["avg_value"] = stage_data["total_value"] / stage_data["deals_count"]
        
        print(f"DEBUG: Dados processados para {len(stage_details)} etapas")
        return stage_details
        
    except Exception as e:
        print(f"DEBUG: Exception em fetch_house_stage_details: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_all_funnel_data(base_url: str, token: str, start_date: str, end_date: str):
    """Busca dados de todos os funis para comparar usuários"""
    try:
        # Buscar deals de todos os funis
        url = f"{base_url.rstrip('/')}/api/v1/deals"
        headers = {"accept": "application/json"}
        
        params = {
            "token": token,
            "start_date": start_date,
            "end_date": end_date,
            "limit": 200  # Aumentar limite para pegar mais dados
        }
        
        print(f"DEBUG: Buscando todos os deals em: {url}")
        print(f"DEBUG: Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"DEBUG: Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Total de deals encontrados: {len(data.get('deals', []))}")
            return data
        else:
            print(f"DEBUG: Erro na requisição - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        return None

@st.cache_data(ttl=300)
def process_comparative_funnel_data(deals_data):
    """Processa dados para criar gráfico comparativo por usuário"""
    try:
        if not deals_data or "deals" not in deals_data:
            return None
        
        deals = deals_data["deals"]
        
        # Definir usuários de interesse
        target_users = ["Maria Eduarda ", "Paola Chagas"]
        
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
                    user_name = user_info["name"]
                    
                    # Verificar se é um dos usuários de interesse
                    if user_name in target_users:
                        # Obter etapa do deal
                        deal_stage = deal.get("deal_stage", {})
                        stage_name = deal_stage.get("name", "Sem Etapa")
                        
                        # Inicializar contador se não existir
                        if stage_name not in user_stage_data[user_name]:
                            user_stage_data[user_name][stage_name] = 0
                        
                        # Incrementar contador
                        user_stage_data[user_name][stage_name] += 1
        
        # Criar dados para o gráfico
        chart_data = []
        
        # Coletar todas as etapas únicas
        all_stages = set()
        for user_data in user_stage_data.values():
            all_stages.update(user_data.keys())
        
        # Definir todas as etapas do Funil - HOUSE na ordem correta
        stage_order = [
            "LEADs", "LIGAÇÃO 1", "MENSAGEM", "LIGAÇÃO 2", "FOLLOW UP", 
            "AGENDAMENTO", "ATENDIMENTO REALIZADO", "NEGOCIAÇÃO", "FECHAMENTO", "PERDIDA"
        ]
        
        # Remover duplicatas e garantir que apenas etapas únicas sejam incluídas
        final_stage_order = []
        for stage in stage_order:
            if stage not in final_stage_order:
                final_stage_order.append(stage)
        
        # Adicionar etapas que não estão na ordem padrão (se houver)
        for stage in all_stages:
            if stage not in final_stage_order:
                final_stage_order.append(stage)
        
        stage_order = final_stage_order
        
        # Criar dados para cada usuário e etapa
        for user in target_users:
            for stage in stage_order:
                count = user_stage_data[user].get(stage, 0)
                chart_data.append({
                    "Usuário": user,
                    "Etapa": stage,
                    "Quantidade": count
                })
        
        return pd.DataFrame(chart_data)
        
    except Exception as e:
        print(f"DEBUG: Exception em process_comparative_funnel_data: {str(e)}")
        return None

# -------- Indicador de Última Atualização --------
def show_last_update():
    """Mostra quando os dados foram atualizados pela última vez"""
    from datetime import datetime
    now = datetime.now()
    st.caption(f"🕐 Última atualização: {now.strftime('%d/%m/%Y %H:%M:%S')}")

# -------- Header --------
st.title("🏠 Dashboard Funil - HOUSE")
st.caption("Análise específica do Funil - HOUSE (ID: 689b59706e704a0024fc2374)")

# -------- Sidebar --------
with st.sidebar:
    st.header("⚙️ Configuração")
    
    # Configuração da API
    base_url = st.text_input("API Base URL", os.getenv("API_BASE_URL", "https://crm.rdstation.com"))
    token = st.text_input("API Token", os.getenv("API_TOKEN", "681cb285978e2f00145fb15d"), type="password")
    
    st.divider()
    
    # Informações do Funil - HOUSE
    st.subheader("🏠 Funil - HOUSE")
    st.info("**ID:** `689b59706e704a0024fc2374`")
    st.success("✅ Dashboard focado no Funil - HOUSE")
    
    st.divider()
    
    # Período de análise
    st.subheader("🗓️ Período de Análise")
    today = date.today()
    start_default = today - timedelta(days=30)
    d_start = st.date_input("Data Início", start_default, format="DD/MM/YYYY")
    d_end = st.date_input("Data Fim", today, format="DD/MM/YYYY")
    
    st.divider()
    
    # Filtros
    st.subheader("🎯 Filtros")
    team_filter = st.selectbox(
        "Selecionar Time",
        ["Todos", "Equipe Fenix", "Equipe Bulls"],
        help="Escolha um time específico ou veja todos os dados do Funil - HOUSE"
    )
    
    st.divider()
    
    # Status da conexão
    if token and base_url:
        st.success("✅ Conectado ao CRM")
        st.info(f"📅 Período: {d_start.strftime('%d/%m/%Y')} - {d_end.strftime('%d/%m/%Y')}")
        st.info("🏠 Funil: HOUSE")
    else:
        st.warning("⚠️ Configure a API")

    st.divider()
    
    # Configurações de Auto-Refresh
    st.subheader("🔄 Auto-Refresh")
    auto_refresh = st.checkbox(
        "Ativar atualização automática",
        value=True,
        help="Atualiza os dados automaticamente"
    )
    
    if auto_refresh:
        refresh_interval = st.selectbox(
            "Intervalo de atualização:",
            ["30 segundos", "1 minuto", "2 minutos", "5 minutos", "10 minutos"],
            index=2,  # 2 minutos como padrão
            help="Frequência de atualização dos dados"
        )
        
        # Converter para segundos
        interval_map = {
            "30 segundos": 30,
            "1 minuto": 60,
            "2 minutos": 120,
            "5 minutos": 300,
            "10 minutos": 600
        }
        
        refresh_seconds = interval_map[refresh_interval]
        
        # Mostrar status do auto-refresh
        st.success(f"✅ Auto-refresh ativo - {refresh_interval}")
        
        # Botão de atualização manual
        if st.button("🔄 Atualizar Agora", help="Força uma atualização imediata dos dados"):
            st.rerun()
        
        # Adicionar JavaScript para auto-refresh
        st.markdown(
            f"""
            <script>
                setTimeout(function(){{
                    window.location.reload();
                }}, {refresh_seconds * 1000});
            </script>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("ℹ️ Auto-refresh desativado")
        
        # Botão de atualização manual quando auto-refresh está desativado
        if st.button("🔄 Atualizar Agora", help="Força uma atualização imediata dos dados"):
            st.rerun()
    
    st.divider()

# -------- Tabs --------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Consulta de Estágios - Funil HOUSE", "📈 Detalhes das Etapas - HOUSE", "👥 Comparativo por Usuário"])

# -------- Aba 1: Dashboard --------
with tab1:
    if token and base_url:
        # Mostrar última atualização
        show_last_update()
        
        # Converter datas para string
        start_date = d_start.strftime("%Y-%m-%d")
        end_date = d_end.strftime("%Y-%m-%d")
        
        # -------- Informações do Funil - HOUSE --------
        st.subheader("🏠 Funil - HOUSE - Informações")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏠 Funil", "HOUSE")
        with col2:
            st.metric("🆔 ID", "689b59706e704a0024fc2374")
        with col3:
            st.metric("📊 Status", "Ativo")
        
        st.divider()
        
        # Buscar dados específicos do Funil - HOUSE
        with st.spinner("🔄 Carregando dados do Funil - HOUSE..."):
            house_data = fetch_house_funnel_data(base_url, token, start_date, end_date)
            
            if house_data:
                # Processar dados
                funnel_df = process_deals_data(house_data, team_filter)
                
                if funnel_df is not None and not funnel_df.empty:
                    # -------- Métricas Principais --------
                    st.header("📈 Métricas do Funil - HOUSE")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_deals = funnel_df["count"].sum()
                        st.metric("Total de Negócios", total_deals)
                    
                    with col2:
                        if len(funnel_df) > 1:
                            conversion_rate = (funnel_df.iloc[-1]["count"] / funnel_df.iloc[0]["count"] * 100) if funnel_df.iloc[0]["count"] > 0 else 0
                            st.metric("Taxa de Conversão", f"{conversion_rate:.1f}%")
                        else:
                            st.metric("Taxa de Conversão", "N/A")
                    
                    with col3:
                        stages_count = len(funnel_df)
                        st.metric("Estágios Ativos", stages_count)
                    
                    with col4:
                        avg_deals_per_stage = total_deals / stages_count if stages_count > 0 else 0
                        st.metric("Média por Estágio", f"{avg_deals_per_stage:.0f}")
                    
                    st.divider()
                    
                    # -------- Funil de Vendas - HOUSE --------
                    st.header(f"📊 Funil de Vendas - HOUSE ({team_filter})")
                    
                    # Gráfico de barras
                    st.bar_chart(funnel_df.set_index("stage"), use_container_width=True)
                    
                    # Tabela detalhada
                    st.subheader("📋 Detalhamento por Estágio")
                    st.dataframe(funnel_df, use_container_width=True)
                    
                    # Download dos dados
                    csv = funnel_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV - HOUSE",
                        data=csv,
                        file_name=f"house_funnel_{team_filter}_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                    
                    st.divider()
                    
                    # -------- Análise por Usuário --------
                    if team_filter == "Todos":
                        st.header("👥 Análise por Usuário - HOUSE")
                        
                        # Contar por usuário
                        user_counts = {}
                        for deal in house_data["deals"]:
                            if "user" in deal and deal["user"]:
                                user_info = deal["user"]
                                if isinstance(user_info, dict) and "name" in user_info:
                                    user_name = user_info["name"]
                                    if user_name not in user_counts:
                                        user_counts[user_name] = 0
                                    user_counts[user_name] += 1
                        
                        if user_counts:
                            # Criar gráfico de usuários
                            user_df = pd.DataFrame([
                                {"Usuário": user, "Negócios": count}
                                for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
                            ])
                            
                            st.bar_chart(user_df.set_index("Usuário"), use_container_width=True)
                            
                            # Tabela de usuários
                            st.dataframe(user_df, use_container_width=True)
                
                else:
                    st.error("❌ Não foi possível processar os dados do Funil - HOUSE")
                    st.info("💡 Verifique se a API retornou dados válidos")
            else:
                st.error("❌ Falha ao conectar com o Funil - HOUSE")
                st.info("💡 Verifique a URL base e o token")
    else:
        st.info("ℹ️ Configure a URL base e o token na sidebar para ver os dados do Funil - HOUSE")

# -------- Aba 2: Consulta de Estágios --------
with tab2:
    if token and base_url:
        # Mostrar última atualização
        show_last_update()
        
        st.header("🔍 Consulta de Estágios - Funil HOUSE")
        st.caption("Explore a estrutura de etapas do Funil - HOUSE (ID: 689b59706e704a0024fc2374)")
        
        if token and base_url:
            # Seção de debug
            with st.expander("🔧 Debug - Informações da API"):
                st.write(f"**URL Base:** {base_url}")
                st.write(f"**Token:** {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
                st.write(f"**Funil HOUSE ID:** `689b59706e704a0024fc2374`")
                st.write(f"**URL Completa:** {base_url.rstrip('/')}/api/v1/deal_stages")
                
                # Testar conectividade básica
                if st.button("🧪 Testar Conectividade", key="test_connectivity"):
                    try:
                        test_url = f"{base_url.rstrip('/')}/api/v1/deal_stages"
                        test_headers = {"accept": "application/json"}
                        test_params = {"token": token}
                        
                        st.write("**Testando com token como parâmetro:**")
                        st.code(f"GET {test_url}?token={token[:10]}...")
                        
                        response = requests.get(test_url, headers=test_headers, params=test_params, timeout=10)
                        
                        st.write(f"**Status Code:** {response.status_code}")
                        st.write(f"**Response:** {response.text[:200]}...")
                        
                        if response.status_code == 200:
                            st.success("✅ Conexão bem-sucedida!")
                        else:
                            st.error(f"❌ Erro {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Erro na conexão: {str(e)}")
            
            # Buscar etapas do Funil - HOUSE
            if st.button("🎯 Buscar Etapas do Funil - HOUSE", key="fetch_house_stages"):
                with st.spinner("🔄 Consultando etapas do Funil - HOUSE..."):
                    # Debug: Mostrar informações da requisição
                    st.write("**🔍 Debug da Requisição:**")
                    st.write(f"URL: `{base_url.rstrip('/')}/api/v1/deal_stages`")
                    st.write(f"Token: `{token[:10]}...{token[-10:] if len(token) > 20 else '***'}`")
                    
                    house_stages_data = fetch_house_funnel_stages(base_url, token)
                    
                    # Debug: Mostrar resultado da função
                    st.write("**🔍 Resultado da Função:**")
                    if house_stages_data is None:
                        st.error("❌ Função retornou None")
                        st.info("💡 Verifique os logs do console para mais detalhes")
                    elif isinstance(house_stages_data, dict) and "house_stages" in house_stages_data:
                        st.warning(f"⚠️ Nenhuma etapa do HOUSE encontrada!")
                        st.info(f"💡 Mostrando todas as etapas disponíveis para debug.")
                        
                        # Mostrar informações de debug
                        st.write("**🔍 Informações de Debug:**")
                        st.write(f"**Total de etapas na API:** {len(house_stages_data['all_stages'])}")
                        st.write(f"**Pipelines encontrados:** {len(house_stages_data['all_pipelines'])}")
                        
                        # Mostrar todos os pipelines
                        st.write("**📋 Todos os Pipelines Disponíveis:**")
                        for i, pipeline in enumerate(house_stages_data['all_pipelines'], 1):
                            st.write(f"{i}. {pipeline}")
                        
                        # Mostrar todas as etapas
                        st.write("**📋 Todas as Etapas Disponíveis:**")
                        all_stages_summary = []
                        for stage in house_stages_data['all_stages']:
                            if isinstance(stage, dict):
                                pipeline_info = stage.get("deal_pipeline", {})
                                all_stages_summary.append({
                                    "Nome": stage.get("name", "N/A"),
                                    "Apelido": stage.get("nickname", "N/A"),
                                    "ID": stage.get("id", "N/A"),
                                    "Ordem": stage.get("order", "N/A"),
                                    "Pipeline": pipeline_info.get("name", "N/A"),
                                    "Pipeline ID": pipeline_info.get("id", "N/A")
                                })
                        
                        if all_stages_summary:
                            all_stages_df = pd.DataFrame(all_stages_summary)
                            st.dataframe(all_stages_df, use_container_width=True)
                            
                            # Download de todas as etapas
                            csv = all_stages_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Todas as Etapas",
                                data=csv,
                                file_name=f"all_stages_{date.today().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                        
                        st.error("❌ O Funil - HOUSE (ID: 689b59706e704a0024fc2374) não foi encontrado nas etapas disponíveis.")
                        st.info("💡 Verifique se o ID do funil está correto ou se o funil existe no RD Station.")
                        
                    elif isinstance(house_stages_data, list):
                        st.success(f"✅ Função retornou lista com {len(house_stages_data)} itens")
                        
                        if house_stages_data:
                            st.success(f"✅ {len(house_stages_data)} etapas do Funil - HOUSE encontradas!")
                            
                            # -------- Debug: Mostrar todas as etapas encontradas --------
                            with st.expander("🔍 Debug - Todas as Etapas Encontradas"):
                                try:
                                    # Buscar todas as etapas para debug
                                    all_stages_url = f"{base_url.rstrip('/')}/api/v1/deal_stages"
                                    all_stages_headers = {"accept": "application/json"}
                                    all_stages_params = {"token": token}
                                    
                                    all_stages_response = requests.get(all_stages_url, headers=all_stages_headers, params=all_stages_params, timeout=30)
                                    
                                    if all_stages_response.status_code == 200:
                                        all_stages_data = all_stages_response.json()
                                        
                                        if "deal_stages" in all_stages_data:
                                            st.write(f"**📊 Total de etapas na API:** {len(all_stages_data['deal_stages'])}")
                                            
                                            # Mostrar todas as etapas e seus pipelines
                                            st.write("**🔍 Todas as etapas e seus pipelines:**")
                                            for i, stage in enumerate(all_stages_data["deal_stages"], 1):
                                                pipeline_info = stage.get("deal_pipeline", {})
                                                pipeline_id = pipeline_info.get("id", "N/A")
                                                pipeline_name = pipeline_info.get("name", "N/A")
                                                
                                                # Destacar se é do HOUSE
                                                if pipeline_id == "689b59706e704a0024fc2374":
                                                    st.write(f"**🏠 {i}. {stage.get('name', 'N/A')}** - Pipeline: {pipeline_name} (ID: {pipeline_id}) ✅")
                                                else:
                                                    st.write(f"{i}. {stage.get('name', 'N/A')} - Pipeline: {pipeline_name} (ID: {pipeline_id})")
                                            
                                            st.divider()
                                            st.write(f"**🎯 Etapas filtradas para HOUSE:** {len(house_stages_data)}")
                                            
                                except Exception as e:
                                    st.error(f"❌ Erro no debug: {str(e)}")
                            
                            # -------- Análise da Estrutura dos Dados --------
                            with st.expander("🔍 Análise da Estrutura dos Dados"):
                                st.write("**📋 Estrutura das etapas do Funil - HOUSE:**")
                                
                                # Mostrar estrutura do primeiro item
                                if house_stages_data:
                                    first_stage = house_stages_data[0]
                                    st.write("**Primeiro item da resposta:**")
                                    st.json(first_stage)
                                    
                                    st.write("**🔍 Campos disponíveis:**")
                                    for key, value in first_stage.items():
                                        if isinstance(value, list):
                                            st.write(f"- **{key}**: Lista com {len(value)} itens")
                                            if value:
                                                st.write(f"  - Primeiro item: {value[0]}")
                                        else:
                                            st.write(f"- **{key}**: {value}")
                            
                            # -------- Etapas do Funil - HOUSE --------
                            st.subheader("🏠 Etapas do Funil - HOUSE")
                            st.caption("Dados específicos do Funil - HOUSE")
                            
                            # Criar tabela das etapas
                            if house_stages_data:
                                stages_summary = []
                                for stage in house_stages_data:
                                    if isinstance(stage, dict):
                                        # Extrair informações do pipeline
                                        pipeline_info = stage.get("deal_pipeline", {})
                                        
                                        stages_summary.append({
                                            "Nome": stage.get("name", "N/A"),
                                            "Apelido": stage.get("nickname", "N/A"),
                                            "ID": stage.get("id", "N/A"),
                                            "Ordem": stage.get("order", "N/A"),
                                            "Pipeline": pipeline_info.get("name", "N/A"),
                                            "Pipeline ID": pipeline_info.get("id", "N/A"),
                                            "Objetivo": stage.get("objective", "N/A")[:50] + "..." if stage.get("objective") and len(stage.get("objective", "")) > 50 else stage.get("objective", "N/A")
                                        })
                                
                                if stages_summary:
                                    stages_df = pd.DataFrame(stages_summary)
                                    st.dataframe(stages_df, use_container_width=True)
                                    
                                    # Download das etapas
                                    csv = stages_df.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Etapas - HOUSE",
                                        data=csv,
                                        file_name=f"house_stages_{date.today().strftime('%Y%m%d')}.csv",
                                        mime="text/csv"
                                    )
                                    
                                    # Mostrar detalhes das etapas
                                    st.subheader("📊 Detalhes das Etapas - HOUSE")
                                    
                                    for i, stage in enumerate(house_stages_data, 1):
                                        with st.expander(f"🎯 {i}. {stage.get('name', 'N/A')} (Ordem: {stage.get('order', 'N/A')})"):
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                st.write(f"**Nome:** {stage.get('name', 'N/A')}")
                                                st.write(f"**Apelido:** {stage.get('nickname', 'N/A')}")
                                                st.write(f"**ID:** `{stage.get('id', 'N/A')}`")
                                                st.write(f"**Ordem:** {stage.get('order', 'N/A')}")
                                            
                                            with col2:
                                                pipeline_info = stage.get("deal_pipeline", {})
                                                st.write(f"**Pipeline:** {pipeline_info.get('name', 'N/A')}")
                                                st.write(f"**Pipeline ID:** {pipeline_info.get('id', 'N/A')}")
                                                
                                                if stage.get('objective'):
                                                    st.write("**Objetivo:**")
                                                    st.info(stage.get('objective'))
                                                
                                                if stage.get('description'):
                                                    st.write("**Descrição:**")
                                                    st.text(stage.get('description'))
                        else:
                            st.warning("⚠️ Lista vazia retornada")
                    else:
                        st.warning(f"⚠️ Função retornou tipo inesperado: {type(house_stages_data)}")
                    
                    if not house_stages_data or (isinstance(house_stages_data, list) and len(house_stages_data) == 0):
                        st.error("❌ Falha ao buscar etapas do Funil - HOUSE")
                        st.info("💡 Verifique se o token tem permissões para acessar o funil")
                        
                        # Mostrar informações de debug
                        st.subheader("🔧 Informações de Debug")
                        st.info("💡 Abra a seção 'Debug - Informações da API' acima para mais detalhes")
        else:
            st.info("ℹ️ Configure a URL base e o token na sidebar para consultar os estágios do Funil - HOUSE")

# -------- Aba 3: Detalhes das Etapas - HOUSE --------
with tab3:
    if token and base_url:
        # Mostrar última atualização
        show_last_update()
        
        st.header("📈 Detalhes das Etapas - Funil HOUSE")
        
        # Converter datas para string
        start_date = d_start.strftime("%Y-%m-%d")
        end_date = d_end.strftime("%Y-%m-%d")
        
        # Buscar dados detalhados das etapas
        stage_details = fetch_house_stage_details(base_url, token, start_date, end_date)
        
        if stage_details:
            # Ordenar etapas por ordem
            sorted_stages = sorted(stage_details.values(), key=lambda x: x["order"])
            
            # Coletar todos os usuários únicos
            all_users = set()
            for stage in sorted_stages:
                for deal in stage["deals"]:
                    all_users.add(deal["user"])
            
            all_users = sorted(list(all_users))
            
            # Debug: Mostrar todos os usuários encontrados
            st.info(f"🔍 Usuários encontrados nos dados: {all_users}")
            st.info(f"📊 Total de usuários únicos: {len(all_users)}")
            
            # Filtro por usuário
            st.subheader("👥 Filtro por Usuário")
            selected_user = st.selectbox(
                "Selecione um usuário para filtrar:",
                ["Todos os Usuários"] + all_users,
                help="Filtrar deals por quem criou a informação"
            )
            
            # Aplicar filtro
            if selected_user != "Todos os Usuários":
                # Filtrar deals por usuário
                filtered_stages = {}
                for stage_id, stage_data in stage_details.items():
                    filtered_deals = [deal for deal in stage_data["deals"] if deal["user"] == selected_user]
                    
                    filtered_stages[stage_id] = {
                        **stage_data,
                        "deals": filtered_deals,
                        "deals_count": len(filtered_deals),
                        "total_value": sum(deal["value"] for deal in filtered_deals),
                        "avg_value": sum(deal["value"] for deal in filtered_deals) / len(filtered_deals) if filtered_deals else 0
                    }
                
                # Atualizar sorted_stages com dados filtrados
                sorted_stages = sorted(filtered_stages.values(), key=lambda x: x["order"])
                
                st.success(f"✅ Filtrado por: {selected_user}")
            else:
                st.info("ℹ️ Mostrando dados de todos os usuários")
            
            st.divider()
            
            # Métricas gerais (com filtro aplicado)
            total_deals = sum(stage["deals_count"] for stage in sorted_stages)
            total_value = sum(stage["total_value"] for stage in sorted_stages)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total de Deals", total_deals)
            with col2:
                st.metric("💰 Valor Total", f"R$ {total_value:,.2f}")
            with col3:
                avg_value = total_value / total_deals if total_deals > 0 else 0
                st.metric("📈 Valor Médio", f"R$ {avg_value:,.2f}")
            
            st.divider()
            
            # Gráfico de barras das etapas
            st.subheader("📊 Distribuição por Etapa")
            
            # Preparar dados para o gráfico
            stage_names = [stage["name"] for stage in sorted_stages]
            stage_counts = [stage["deals_count"] for stage in sorted_stages]
            stage_values = [stage["total_value"] for stage in sorted_stages]
            
            # Gráfico de quantidade de deals
            fig_count = go.Figure(data=[
                go.Bar(
                    x=stage_names,
                    y=stage_counts,
                    text=stage_counts,
                    textposition='auto',
                    marker_color='lightblue',
                    name='Quantidade de Deals'
                )
            ])
            fig_count.update_layout(
                title=f"Quantidade de Deals por Etapa{f' - {selected_user}' if selected_user != 'Todos os Usuários' else ''}",
                xaxis_title="Etapas",
                yaxis_title="Quantidade",
                height=400
            )
            st.plotly_chart(fig_count, use_container_width=True)
            
            # Gráfico de valores
            fig_value = go.Figure(data=[
                go.Bar(
                    x=stage_names,
                    y=stage_values,
                    text=[f"R$ {v:,.2f}" for v in stage_values],
                    textposition='auto',
                    marker_color='lightgreen',
                    name='Valor Total'
                )
            ])
            fig_value.update_layout(
                title=f"Valor Total por Etapa{f' - {selected_user}' if selected_user != 'Todos os Usuários' else ''}",
                xaxis_title="Etapas",
                yaxis_title="Valor (R$)",
                height=400
            )
            st.plotly_chart(fig_value, use_container_width=True)
            
            st.divider()
            
            # Tabela detalhada
            st.subheader("📋 Tabela Detalhada das Etapas")
            
            # Criar DataFrame para a tabela
            table_data = []
            for stage in sorted_stages:
                table_data.append({
                    "Ordem": stage["order"],
                    "Etapa": stage["name"],
                    "Apelido": stage["nickname"],
                    "Deals": stage["deals_count"],
                    "Valor Total": f"R$ {stage['total_value']:,.2f}",
                    "Valor Médio": f"R$ {stage['avg_value']:,.2f}",
                    "ID": stage["id"]
                })
            
            df_stages = pd.DataFrame(table_data)
            st.dataframe(df_stages, use_container_width=True)
            
            # Download da tabela
            csv = df_stages.to_csv(index=False)
            filter_suffix = f"_{selected_user.replace(' ', '_')}" if selected_user != "Todos os Usuários" else ""
            st.download_button(
                label="📥 Download Tabela Detalhada",
                data=csv,
                file_name=f"detalhes_etapas_house{filter_suffix}_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
            
            st.divider()
            
            # Resumo de performance por usuário
            st.subheader("👥 Resumo de Performance por Usuário")
            
            # Calcular métricas por usuário
            user_performance = {}
            for stage in stage_details.values():
                for deal in stage["deals"]:
                    user = deal["user"]
                    if user not in user_performance:
                        user_performance[user] = {
                            "total_deals": 0,
                            "total_value": 0,
                            "stages": set()
                        }
                    
                    user_performance[user]["total_deals"] += 1
                    user_performance[user]["total_value"] += deal["value"]
                    user_performance[user]["stages"].add(stage["name"])
            
            # Criar DataFrame de performance
            performance_data = []
            for user, metrics in user_performance.items():
                performance_data.append({
                    "Usuário": user,
                    "Total Deals": metrics["total_deals"],
                    "Valor Total": f"R$ {metrics['total_value']:,.2f}",
                    "Valor Médio": f"R$ {metrics['total_value']/metrics['total_deals']:,.2f}" if metrics["total_deals"] > 0 else "R$ 0,00",
                    "Etapas Ativas": len(metrics["stages"]),
                    "Etapas": ", ".join(sorted(metrics["stages"]))
                })
            
            # Ordenar por valor total
            performance_data.sort(key=lambda x: float(x["Valor Total"].replace("R$ ", "").replace(",", "")), reverse=True)
            
            df_performance = pd.DataFrame(performance_data)
            st.dataframe(df_performance, use_container_width=True)
            
            # Gráfico de performance por usuário
            if len(performance_data) > 1:
                users = [row["Usuário"] for row in performance_data]
                values = [float(row["Valor Total"].replace("R$ ", "").replace(",", "")) for row in performance_data]
                deals = [row["Total Deals"] for row in performance_data]
                
                fig_user = go.Figure(data=[
                    go.Bar(
                        x=users,
                        y=values,
                        text=[f"R$ {v:,.2f}" for v in values],
                        textposition='auto',
                        marker_color='lightcoral',
                        name='Valor Total'
                    )
                ])
                fig_user.update_layout(
                    title="Performance por Usuário - Valor Total",
                    xaxis_title="Usuários",
                    yaxis_title="Valor (R$)",
                    height=400
                )
                st.plotly_chart(fig_user, use_container_width=True)
            
            st.divider()
            
            # Detalhes de cada etapa
            st.subheader("🔍 Detalhes de Cada Etapa")
            
            for stage in sorted_stages:
                if stage["deals_count"] > 0:
                    with st.expander(f"📋 {stage['name']} ({stage['deals_count']} deals)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Deals", stage["deals_count"])
                        with col2:
                            st.metric("Valor Total", f"R$ {stage['total_value']:,.2f}")
                        with col3:
                            st.metric("Valor Médio", f"R$ {stage['avg_value']:,.2f}")
                        
                        # Lista de deals da etapa
                        st.subheader("📝 Deals desta Etapa")
                        deals_df = pd.DataFrame(stage["deals"])
                        if not deals_df.empty:
                            # Formatar colunas
                            deals_df["value"] = deals_df["value"].apply(lambda x: f"R$ {x:,.2f}")
                            deals_df["created_at"] = pd.to_datetime(deals_df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                            deals_df = deals_df.rename(columns={
                                "id": "ID",
                                "name": "Nome",
                                "value": "Valor",
                                "user": "Usuário",
                                "created_at": "Criado em"
                            })
                            st.dataframe(deals_df, use_container_width=True)
                        else:
                            st.info("Nenhum deal encontrado nesta etapa.")
                else:
                    with st.expander(f"📋 {stage['name']} (0 deals)"):
                        st.info("Nenhum deal encontrado nesta etapa.")
        else:
            st.error("❌ Erro ao buscar detalhes das etapas")
    else:
        st.warning("⚠️ Configure a API")

# -------- Aba 4: Comparativo por Usuário --------
with tab4:
    if token and base_url:
        # Mostrar última atualização
        show_last_update()
        
        st.header("👥 Comparativo por Usuário - Funil HOUSE")
        st.caption("Análise comparativa de negócios entre usuários do Funil - HOUSE")
        
        # Converter datas para string
        start_date = d_start.strftime("%Y-%m-%d")
        end_date = d_end.strftime("%Y-%m-%d")
        
        # Buscar dados comparativos
        comparative_data = fetch_all_funnel_data(base_url, token, start_date, end_date)
        
        if comparative_data:
            # Processar dados para o gráfico comparativo
            comparative_df = process_comparative_funnel_data(comparative_data)
            
            if comparative_df is not None and not comparative_df.empty:
                # Criar gráfico de barras empilhadas
                st.subheader("📊 Comparativo de Negócios por Usuário")
                
                # Definir cores para cada usuário
                colors = {
                    "Maria Eduarda ": "lightcoral",  # Vermelho pastel
                    "Paola Chagas": "lightblue"      # Azul pastel
                }
                
                fig = go.Figure()
                
                for user in comparative_df["Usuário"].unique():
                    user_data = comparative_df[comparative_df["Usuário"] == user]
                    fig.add_trace(go.Bar(
                        x=user_data["Etapa"],
                        y=user_data["Quantidade"],
                        text=user_data["Quantidade"],  # Mostrar valores em cima das barras
                        textposition='auto',  # Posicionamento automático
                        name=user,
                        marker_color=colors.get(user, "gray") # Cor padrão se não encontrada
                    ))
                
                fig.update_layout(
                    title="Quantidade de Negócios por Etapa por Usuário",
                    xaxis_title="Etapas",
                    yaxis_title="Quantidade",
                    barmode='group', # Barras lado a lado
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
                            text=user_data["Quantidade"],  # Mostrar valores em cima das barras
                            textposition='auto',  # Posicionamento automático
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
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tabela detalhada
                st.subheader("📋 Detalhamento Comparativo")
                st.dataframe(comparative_df, use_container_width=True)
                
                # Download dos dados
                csv = comparative_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Comparativo",
                    data=csv,
                    file_name=f"comparativo_usuarios_house_{start_date}_to_{end_date}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Não foi possível processar os dados para o gráfico comparativo.")
        else:
            st.error("❌ Falha ao conectar com o CRM para buscar dados comparativos.")
    else:
        st.info("ℹ️ Configure a URL base e o token na sidebar para ver o comparativo por usuário.")

# -------- Informações --------
with st.expander("ℹ️ Sobre o Dashboard"):
    st.write("""
    **Dashboard CRM - RD Station**
    
    Este dashboard analisa dados de negócios do RD Station CRM e cria visualizações de funis de vendas.
    
    **Funcionalidades:**
    - 📊 Gráfico de funil de vendas
    - 👥 Análise por usuário
    - 📈 Métricas de conversão
    - 📥 Download dos dados
    - 🔍 Consulta de estágios dos funis
    
    **Estágios do Funil:**
    - **Leads**: Rating 1
    - **MQL**: Rating 2  
    - **SQL**: Rating 3
    - **Proposta**: Rating 4
    - **Negociação**: Rating 5
    - **Em Andamento**: Outros ratings
    """)
