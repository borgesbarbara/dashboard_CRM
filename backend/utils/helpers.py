"""
Funções utilitárias para o sistema
"""
from datetime import datetime
import streamlit as st
from typing import List, Dict
import hashlib


def show_last_update():
    """Mostra quando os dados foram atualizados pela última vez"""
    now = datetime.now()
    st.caption(f"🕐 Última atualização: {now.strftime('%d/%m/%Y %H:%M:%S')}")


def format_date_range(start_date, end_date):
    """Formata intervalo de datas para exibição"""
    return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"


def get_stage_color(stage_name: str) -> str:
    """Retorna cor para cada etapa do funil"""
    colors = {
        "LEADs": "#FF6B6B",
        "LIGAÇÃO 1": "#4ECDC4", 
        "MENSAGEM": "#45B7D1",
        "LIGAÇÃO 2": "#96CEB4",
        "FOLLOW UP": "#FFEAA7",
        "AGENDAMENTO": "#DDA0DD",
        "ATENDIMENTO REALIZADO": "#98D8C8",
        "NEGOCIAÇÃO": "#F7DC6F",
        "FECHAMENTO": "#BB8FCE",
        "PERDIDA": "#E74C3C"
    }
    return colors.get(stage_name, "#95A5A6")


def get_user_color(user_name: str) -> str:
    """Retorna cor para cada usuário"""
    # Cores personalizadas conforme solicitado
    custom_colors = {
        "Maria Eduarda": "#FFB6C1",  # Vermelho pastel
        "Maria Eduarda ": "#FFB6C1",  # Vermelho pastel (com espaço)
        "Paola Chagas": "#4682B4",    # Azul escuro pastel
        "David Cauã Ferreira de Sene": "#FFB347",  # Laranja pastel
        "Renata Cavalheiro": "#87CEEB",
        "Renata Cavalheiro ": "#87CEEB"

    }
    
    # Se tem cor personalizada, usar ela
    if user_name in custom_colors:
        return custom_colors[user_name]
    
    # Para todos os demais usuários, usar amarelo pastel
    return "#F0E68C"  # Amarelo pastel


def generate_user_colors(users: List[str]) -> Dict[str, str]:
    """Gera cores para uma lista de usuários"""
    colors = {}
    for user in users:
        colors[user] = get_user_color(user)
    return colors


def validate_api_config(base_url: str, token: str) -> bool:
    """Valida se a configuração da API está correta"""
    return bool(base_url and token and len(token) > 10)


def format_file_name(prefix: str, start_date, end_date) -> str:
    """Formata nome de arquivo para download"""
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    return f"{prefix}_{start_str}_to_{end_str}.csv"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca texto se exceder o tamanho máximo"""
    if text and len(text) > max_length:
        return text[:max_length] + "..."
    return text or "N/A" 