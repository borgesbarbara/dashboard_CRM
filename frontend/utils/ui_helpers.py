"""
Funções utilitárias para a interface do usuário
"""
import streamlit as st


def render_info_section():
    """(Removido) Seção de informações do dashboard"""
    pass


def render_error_message(message: str, details: str = None):
    """Renderiza mensagem de erro padronizada"""
    st.error(f"❌ {message}")
    if details:
        st.info(f"💡 {details}")


def render_success_message(message: str):
    """Renderiza mensagem de sucesso padronizada"""
    st.success(f"✅ {message}")


def render_warning_message(message: str):
    """Renderiza mensagem de aviso padronizada"""
    st.warning(f"⚠️ {message}")


def render_info_message(message: str):
    """Renderiza mensagem informativa padronizada"""
    st.info(f"ℹ️ {message}")


def render_loading_spinner(message: str = "Carregando..."):
    """Renderiza spinner de carregamento"""
    return st.spinner(f"🔄 {message}")


def render_metric_card(title: str, value, delta: str = None):
    """Renderiza card de métrica"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            label=title,
            value=value,
            delta=delta
        )


def render_dataframe_with_download(df, title: str, filename: str):
    """Renderiza dataframe com botão de download"""
    st.subheader(title)
    st.dataframe(df, use_container_width=True)
    
    # Download
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def render_json_viewer(data, title: str = "Dados JSON"):
    """Renderiza visualizador de JSON"""
    st.subheader(title)
    st.json(data)


def render_code_block(code: str, language: str = "python"):
    """Renderiza bloco de código"""
    st.code(code, language=language)


def render_divider():
    """Renderiza divisor visual"""
    st.divider()


def render_columns(num_columns: int = 2):
    """Renderiza colunas"""
    return st.columns(num_columns) 