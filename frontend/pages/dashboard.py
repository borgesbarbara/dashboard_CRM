"""
Página principal do dashboard
"""
import streamlit as st
import pandas as pd
from datetime import date
import requests

from backend.api.rd_station_client import RDStationClient
from backend.api.data_processor import DataProcessor
from backend.utils.helpers import show_last_update, format_file_name
from frontend.components.charts import ChartComponents
from frontend.components.filters import FilterComponents, render_debug_section, render_stage_details_section


def render_dashboard_page():
    """Renderiza a página principal do dashboard"""
    st.title("🏠 Dashboard Funil - HOUSE")
    st.caption("Análise específica do Funil - HOUSE (ID: 689b59706e704a0024fc2374)")
    
    # Configurações da API
    base_url, token = FilterComponents.render_api_config()
    
    # Filtros de data
    start_date, end_date = FilterComponents.render_date_filters()
    
    # Status da conexão
    FilterComponents.render_connection_status(base_url, token, start_date, end_date)
    
    # Botão de atualização
    FilterComponents.render_refresh_button()
    
    # (Removido) Botão de debug de funil
    
    # Tabs (apenas Comparativo por Usuário)
    tab = st.tabs(["👥 Comparativo por Usuário"])
    
    # Inicializar clientes
    client = RDStationClient(base_url, token)
    processor = DataProcessor()
    
    # Aba única: Comparativo por Usuário
    with tab[0]:
        render_comparative_tab(client, processor, start_date, end_date)


def render_funnel_debug_section(base_url: str, token: str):
    """Renderiza seção de debug para verificar funis ativos"""
    if not base_url or not token:
        st.error("❌ Configure a URL base e o token primeiro")
        return
    
    st.header("🔍 Debug - Verificação de Funis")
    
    with st.spinner("Buscando informações dos funis..."):
        try:
            # Buscar todos os funis disponíveis
            url = f"{base_url.rstrip('/')}/api/v1/deal_pipelines"
            params = {"token": token}
            
            st.info(f"🌐 **URL da API:** `{url}`")
            st.info(f"🔑 **Token:** `{token[:10]}...`")
            
            response = requests.get(url, headers={"accept": "application/json"}, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ **Status da API:** {response.status_code}")
                
                # Mostrar estrutura dos dados
                st.subheader("📊 Estrutura dos Dados Recebidos")
                st.json(data)
                
                # Buscar deals específicos do HOUSE
                st.subheader("🎯 Deals do Funil HOUSE")
                house_url = f"{base_url.rstrip('/')}/api/v1/deals"
                house_params = {
                    "token": token,
                    "deal_pipeline_id": "689b59706e704a0024fc2374",
                    "limit": 10
                }
                
                house_response = requests.get(house_url, headers={"accept": "application/json"}, params=house_params, timeout=30)
                
                if house_response.status_code == 200:
                    house_data = house_response.json()
                    st.success(f"✅ **Deals HOUSE encontrados:** {len(house_data.get('deals', []))}")
                    
                    if house_data.get('deals'):
                        st.subheader("📋 Primeiros 5 Deals do HOUSE")
                        for i, deal in enumerate(house_data['deals'][:5]):
                            with st.expander(f"Deal {i+1}: {deal.get('name', 'Sem nome')}"):
                                st.json(deal)
                else:
                    st.error(f"❌ **Erro ao buscar deals HOUSE:** {house_response.status_code}")
                    st.text(house_response.text[:500])
                    
            else:
                st.error(f"❌ **Erro na API:** {response.status_code}")
                st.text(response.text[:500])
                
        except Exception as e:
            st.error(f"❌ **Erro:** {str(e)}")
            st.exception(e)


def render_stages_tab(client: RDStationClient, processor: DataProcessor, base_url: str, token: str):
    """Renderiza aba de consulta de estágios"""
    if token and base_url:
        show_last_update()
        
        st.header("🔍 Consulta de Estágios - Funil HOUSE")
        st.caption("Explore a estrutura de etapas do Funil - HOUSE (ID: 689b59706e704a0024fc2374)")
        
        # Seção de debug
        test_button = render_debug_section(base_url, token)
        
        if test_button:
            test_connectivity(client, base_url, token)
        
        # Buscar etapas do Funil - HOUSE
        if st.button("🎯 Buscar Etapas do Funil - HOUSE", key="fetch_house_stages"):
            fetch_and_display_stages(client, processor, base_url, token)
    else:
        st.info("ℹ️ Configure a URL base e o token na sidebar para consultar os estágios do Funil - HOUSE")


def render_comparative_tab(client: RDStationClient, processor: DataProcessor, start_date, end_date):
    """Renderiza aba de comparativo por usuário"""
    if client.token and client.base_url:
        show_last_update()
        
        st.header("👥 Comparativo por Usuário - Funil HOUSE")
        st.caption("Análise comparativa de negócios entre usuários do Funil - HOUSE")
        
        # Converter datas para string
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Buscar dados comparativos - APENAS do Funil HOUSE
        comparative_data = client.fetch_house_funnel_data(start_date_str, end_date_str)
        
        if comparative_data:
            
            # (Removidos) botões de ações
            
            # (Removidos) usuários disponíveis
            
            # Processar dados para o gráfico comparativo
            comparative_df = processor.process_comparative_funnel_data(comparative_data)
            
            if comparative_df is not None and not comparative_df.empty:
                render_comparative_charts(comparative_df, start_date, end_date)
                # (Removida) seção de análise por equipes
            else:
                st.warning("⚠️ Não foi possível processar os dados para o gráfico comparativo.")
        else:
            st.error("❌ Falha ao conectar com o CRM para buscar dados comparativos.")
    else:
        st.info("ℹ️ Configure a URL base e o token na sidebar para ver o comparativo por usuário.")


def test_connectivity(client: RDStationClient, base_url: str, token: str):
    """Testa conectividade com a API"""
    try:
        st.write("**Testando com token como parâmetro:**")
        st.code(f"GET {base_url.rstrip('/')}/api/v1/deal_stages?token={token[:10]}...")
        
        result = client.test_connectivity()
        
        st.write(f"**Status Code:** {result['status_code']}")
        st.write(f"**Response:** {result['response_text']}...")
        
        if result['success']:
            st.success("✅ Conexão bem-sucedida!")
        else:
            st.error(f"❌ Erro {result['status_code']}")
            
    except Exception as e:
        st.error(f"❌ Erro na conexão: {str(e)}")


def fetch_and_display_stages(client: RDStationClient, processor: DataProcessor, base_url: str, token: str):
    """Busca e exibe etapas do funil HOUSE"""
    with st.spinner("🔄 Consultando etapas do Funil - HOUSE..."):
        # Debug: Mostrar informações da requisição
        st.write("**🔍 Debug da Requisição:**")
        st.write(f"URL: `{base_url.rstrip('/')}/api/v1/deal_stages`")
        st.write(f"Token: `{token[:10]}...{token[-10:] if len(token) > 20 else '***'}`")
        
        house_stages_data = client.fetch_house_funnel_stages()
        
        # Debug: Mostrar resultado da função
        st.write("**🔍 Resultado da Função:**")
        if house_stages_data is None:
            st.error("❌ Função retornou None")
            st.info("💡 Verifique os logs do console para mais detalhes")
        elif isinstance(house_stages_data, list):
            st.success(f"✅ Função retornou lista com {len(house_stages_data)} itens")
            
            if house_stages_data:
                st.success(f"✅ {len(house_stages_data)} etapas do Funil - HOUSE encontradas!")
                
                # Debug: Mostrar todas as etapas encontradas
                with st.expander("🔍 Debug - Todas as Etapas Encontradas"):
                    show_all_stages_debug(client, house_stages_data)
                
                # Análise da Estrutura dos Dados
                with st.expander("🔍 Análise da Estrutura dos Dados"):
                    analyze_data_structure(house_stages_data)
                
                # Etapas do Funil - HOUSE
                st.subheader("🏠 Etapas do Funil - HOUSE")
                st.caption("Dados específicos do Funil - HOUSE")
                
                # Criar tabela das etapas
                stages_df = processor.process_stages_data(house_stages_data)
                
                if stages_df is not None:
                    st.dataframe(stages_df, use_container_width=True)
                    
                    # Download das etapas
                    filename = f"house_stages_{date.today().strftime('%Y%m%d')}.csv"
                    render_download_button(stages_df, filename)
                    
                    # Mostrar detalhes das etapas
                    render_stage_details_section(house_stages_data)
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

        st.divider()

        # Seção de análise específica da Paola Chagas
        st.subheader("🔍 Investigação Específica - Paola Chagas")
        st.write("Investigue especificamente os dados da Paola Chagas para comparar com o CRM")
        
        if st.button("🔍 Investigar Dados da Paola Chagas"):
            with st.spinner("Investigando dados da Paola Chagas..."):
                paola_investigation = client.investigate_paola_chagas_data()
                
                if "error" not in paola_investigation:
                    # Exibir resumo
                    comparison = paola_investigation["comparison"]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total de Deals", comparison["total_deals"])
                    with col2:
                        st.metric("Deals no HOUSE", comparison["house_deals"])
                    with col3:
                        st.metric("Deals em Outros Funis", comparison["other_deals"])
                    with col4:
                        team_name = comparison["team_info"].get("team_name", "N/A")
                        st.metric("Equipe", team_name)
                    
                    # Exibir possíveis problemas
                    if comparison["possible_issues"]:
                        st.warning("⚠️ Possíveis Problemas Identificados:")
                        for issue in comparison["possible_issues"]:
                            st.write(f"• {issue}")
                    
                    # Exibir detalhes dos deals
                    if paola_investigation["paola_all_deals"]:
                        st.subheader("📋 Todos os Deals da Paola Chagas")
                        deals_df = pd.DataFrame(paola_investigation["paola_all_deals"])
                        st.dataframe(deals_df, use_container_width=True)
                        
                        # Download dos dados
                        csv = deals_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Dados da Paola Chagas",
                            data=csv,
                            file_name="paola_chagas_deals.csv",
                            mime="text/csv"
                        )
                    
                    # Exibir deals do HOUSE
                    if paola_investigation["paola_house_deals"]:
                        st.subheader("🏠 Deals da Paola no Funil HOUSE")
                        house_deals_df = pd.DataFrame(paola_investigation["paola_house_deals"])
                        st.dataframe(house_deals_df, use_container_width=True)
                    else:
                        st.info("ℹ️ Nenhum deal da Paola encontrado no funil HOUSE")
                    
                    # Exibir informações da equipe
                    if paola_investigation["paola_team_info"]:
                        st.subheader("👥 Informações da Equipe")
                        team_info = paola_investigation["paola_team_info"]
                        st.write(f"**Equipe:** {team_info['team_name']}")
                        st.write(f"**Nome:** {team_info['user_name']}")
                        st.write(f"**Email:** {team_info['user_email']}")
                        st.write(f"**ID do Usuário:** {team_info['user_id']}")
                        st.write(f"**ID da Equipe:** {team_info['team_id']}")
                else:
                    st.error(f"❌ Erro na investigação: {paola_investigation['error']}")
        
        st.divider()


def show_all_stages_debug(client: RDStationClient, house_stages_data):
    """Mostra debug de todas as etapas"""
    try:
        # Buscar todas as etapas para debug
        all_stages_url = f"{client.base_url}/api/v1/deal_stages"
        all_stages_headers = {"accept": "application/json"}
        all_stages_params = {"token": client.token}
        
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


def analyze_data_structure(house_stages_data):
    """Analisa estrutura dos dados"""
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


def render_comparative_charts(comparative_df: pd.DataFrame, start_date, end_date):
    """Renderiza gráficos comparativos"""
    # Criar gráfico de barras empilhadas
    st.subheader("📊 Comparativo de Negócios por Usuário")
    
    # Gráfico principal
    fig = ChartComponents.create_comparative_bar_chart(comparative_df, "group")
    st.plotly_chart(fig, use_container_width=True)
    
    # (Removido) seletor de tipo de visualização e gráfico empilhado
    
    # Tabela detalhada
    # (Removido) Detalhamento Comparativo
    
    # (Removido) botão de download do CSV