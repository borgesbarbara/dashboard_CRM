"""
Componentes de filtros para o frontend
"""
import streamlit as st
from datetime import date, timedelta


class FilterComponents:
    """Componentes para filtros da interface"""
    
    @staticmethod
    def render_date_filters():
        """Define período padrão (sem campos na UI)"""
        today = date.today()
        start_default = today - timedelta(days=30)
        
        # Não renderiza inputs; apenas retorna o período padrão
        start_date = start_default
        end_date = today
        
        return start_date, end_date
    
    @staticmethod
    def render_team_filter():
        """Renderiza filtro de equipe"""
        teams = ["Todos", "Equipe Fenix", "Equipe Bulls"]
        selected_team = st.selectbox(
            "Selecionar Equipe:",
            teams,
            index=0
        )
        return selected_team
    
    @staticmethod
    def render_refresh_button():
        """Renderiza botão de atualização"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Atualizar Dados", help="Força uma atualização imediata dos dados"):
                st.cache_data.clear()
                st.rerun()
    
    @staticmethod
    def render_api_config():
        """Renderiza configurações da API"""
        st.sidebar.header("⚙️ Configurações da API")
        
        base_url = st.sidebar.text_input(
            "URL Base:",
            value="https://crm.rdstation.com",
            help="URL base da API do RD Station"
        )
        
        token = st.sidebar.text_input(
            "Token:",
            value="681cb285978e2f00145fb15d",
            type="password",
            help="Token de autenticação da API"
        )
        
        return base_url, token
    
    @staticmethod
    def render_connection_status(base_url: str, token: str, start_date, end_date):
        """Renderiza status da conexão"""
        if token and base_url:
            st.success(f"✅ Conectado ao CRM | 📅 Período: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')} | 🏠 Funil: HOUSE")
        else:
            st.warning("⚠️ Configure a API no arquivo .env")


def render_debug_section(base_url: str, token: str):
    """Renderiza seção de debug"""
    with st.expander("🔧 Debug - Informações da API"):
        st.write(f"**URL Base:** {base_url}")
        st.write(f"**Token:** {token[:10]}...{token[-10:] if len(token) > 20 else '***'}")
        st.write(f"**Funil HOUSE ID:** `689b59706e704a0024fc2374`")
        st.write(f"**URL Completa:** {base_url.rstrip('/')}/api/v1/deal_stages")
        
        return st.button("🧪 Testar Conectividade", key="test_connectivity")


def render_stage_details_section(stages_data):
    """Renderiza seção de detalhes das etapas"""
    if stages_data:
        st.subheader("📊 Detalhes das Etapas - HOUSE")
        
        for i, stage in enumerate(stages_data, 1):
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