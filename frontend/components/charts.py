"""
Componentes de gráficos para o frontend
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from backend.utils.helpers import generate_user_colors


class ChartComponents:
    """Componentes para criação de gráficos"""
    
    @staticmethod
    def create_comparative_bar_chart(df: pd.DataFrame, chart_type: str = "group") -> go.Figure:
        """Cria gráfico de barras comparativo por usuário"""
        # Gerar cores dinamicamente para todos os usuários
        unique_users = df["Usuário"].unique()
        colors = generate_user_colors(unique_users)
        
        fig = go.Figure()
        
        for user in df["Usuário"].unique():
            user_data = df[df["Usuário"] == user]
            fig.add_trace(go.Bar(
                x=user_data["Etapa"],
                y=user_data["Quantidade"],
                text=user_data["Quantidade"],
                textposition='auto',
                name=user,
                marker_color=colors.get(user, "gray")
            ))
        
        title = "Quantidade de Negócios por Etapa por Usuário"
        if chart_type == "stack":
            title += " (Empilhado)"
        
        fig.update_layout(
            title=title,
            xaxis_title="Etapas",
            yaxis_title="Quantidade",
            barmode=chart_type,
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
        
        return fig
    
    @staticmethod
    def create_funnel_chart(df: pd.DataFrame) -> go.Figure:
        """Cria gráfico de funil de vendas"""
        fig = go.Figure(go.Funnel(
            y=df['stage'],
            x=df['count'],
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(
            title="Funil de Vendas",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        return fig
    
    @staticmethod
    def create_stage_distribution_chart(df: pd.DataFrame) -> go.Figure:
        """Cria gráfico de distribuição por etapas"""
        fig = go.Figure(data=[
            go.Bar(
                x=df['stage'],
                y=df['count'],
                text=df['count'],
                textposition='auto',
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title="Distribuição por Etapas",
            xaxis_title="Etapas",
            yaxis_title="Quantidade",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        return fig

    @staticmethod
    def create_team_comparative_bar_chart(df: pd.DataFrame, chart_type: str = "group") -> go.Figure:
        """Cria gráfico de barras comparativo por equipe"""
        # Gerar cores dinamicamente para todas as equipes
        unique_teams = df["Equipe"].unique()
        colors = generate_user_colors(unique_teams)  # Reutilizar a função de cores
        
        fig = go.Figure()
        
        for team in df["Equipe"].unique():
            team_data = df[df["Equipe"] == team]
            fig.add_trace(go.Bar(
                x=team_data["Etapa"],
                y=team_data["Quantidade"],
                text=team_data["Quantidade"],
                textposition='auto',
                name=team,
                marker_color=colors.get(team, "gray")
            ))
        
        title = "Quantidade de Negócios por Etapa por Equipe"
        if chart_type == "stack":
            title += " (Empilhado)"
        
        fig.update_layout(
            title=title,
            xaxis_title="Etapas",
            yaxis_title="Quantidade",
            barmode=chart_type,
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
        
        return fig


def render_chart_selector():
    """Renderiza seletor de tipo de gráfico"""
    return st.radio(
        "Tipo de Visualização:",
        ["Barras Lado a Lado", "Barras Empilhadas"],
        horizontal=True
    )


def render_download_button(df: pd.DataFrame, filename: str):
    """Renderiza botão de download"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    ) 