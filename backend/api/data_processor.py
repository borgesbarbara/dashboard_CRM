"""
Processador de dados para análise de funis de vendas
"""
import pandas as pd
import streamlit as st
from typing import Optional, Dict, List


class DataProcessor:
    """Processador de dados para análise de funis de vendas"""
    
    @st.cache_data(ttl=300)
    def process_deals_data(_self, deals_data: Dict, selected_team: str = "Todos") -> Optional[pd.DataFrame]:
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
    def process_comparative_funnel_data(_self, deals_data: Dict, target_users: List[str] = None) -> Optional[pd.DataFrame]:
        """Processa dados para criar gráfico comparativo por usuário"""
        try:
            if not deals_data or "deals" not in deals_data:
                return None
            
            deals = deals_data["deals"]
            
            # Se não foram especificados usuários, usar todos os disponíveis
            if target_users is None:
                target_users = _self.get_all_users_from_deals(deals)
            
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

    @st.cache_data(ttl=300)
    def process_team_comparative_data(_self, deals_data: Dict, teams_data: Dict) -> Optional[pd.DataFrame]:
        """Processa dados para criar gráfico comparativo por equipe"""
        try:
            if not deals_data or "deals" not in deals_data:
                return None
            
            deals = deals_data["deals"]
            
            # Criar mapeamento de usuário para equipe
            user_to_team = {}
            for team_name, team_info in teams_data.items():
                for user in team_info.get("users", []):
                    user_to_team[user] = team_name
            
            # Estrutura para armazenar dados por equipe e etapa
            team_stage_data = {}
            
            # Inicializar contadores para cada equipe
            for team_name in teams_data.keys():
                team_stage_data[team_name] = {}
            
            # Processar cada deal
            for deal in deals:
                if "user" in deal and deal["user"]:
                    user_info = deal["user"]
                    if isinstance(user_info, dict) and "name" in user_info:
                        user_name = user_info["name"].strip()
                        
                        # Verificar se o usuário pertence a uma equipe
                        if user_name in user_to_team:
                            team_name = user_to_team[user_name]
                            
                            # Obter etapa do deal
                            deal_stage = deal.get("deal_stage", {})
                            stage_name = deal_stage.get("name", "Sem Etapa")
                            
                            # Inicializar contador se não existir
                            if stage_name not in team_stage_data[team_name]:
                                team_stage_data[team_name][stage_name] = 0
                            
                            # Incrementar contador
                            team_stage_data[team_name][stage_name] += 1
            
            # Criar dados para o gráfico
            chart_data = []
            
            # Coletar todas as etapas únicas
            all_stages = set()
            for team_data in team_stage_data.values():
                all_stages.update(team_data.keys())
            
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
            
            # Criar dados para cada equipe e etapa
            for team_name in teams_data.keys():
                for stage in stage_order:
                    count = team_stage_data[team_name].get(stage, 0)
                    chart_data.append({
                        "Equipe": team_name,
                        "Etapa": stage,
                        "Quantidade": count
                    })
            
            return pd.DataFrame(chart_data)
            
        except Exception as e:
            print(f"DEBUG: Exception em process_team_comparative_data: {str(e)}")
            return None

    def get_all_users_from_deals(self, deals: List[Dict]) -> List[str]:
        """Extrai todos os usuários únicos dos deals"""
        users = set()
        
        for deal in deals:
            if "user" in deal and deal["user"]:
                user_info = deal["user"]
                if isinstance(user_info, dict) and "name" in user_info:
                    user_name = user_info["name"].strip()
                    if user_name:  # Só adicionar se não for vazio
                        users.add(user_name)
        
        return sorted(list(users))

    def process_stages_data(self, stages_data: List) -> Optional[pd.DataFrame]:
        """Processa dados de etapas para exibição em tabela"""
        try:
            if not stages_data:
                return None
            
            stages_summary = []
            for stage in stages_data:
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
                return pd.DataFrame(stages_summary)
            else:
                return None
                
        except Exception as e:
            return None

    def get_stage_order(self) -> List[str]:
        """Retorna a ordem padrão das etapas do Funil - HOUSE"""
        return [
            "LEADs", "LIGAÇÃO 1", "MENSAGEM", "LIGAÇÃO 2", "FOLLOW UP", 
            "AGENDAMENTO", "ATENDIMENTO REALIZADO", "NEGOCIAÇÃO", "FECHAMENTO", "PERDIDA"
        ]

    def get_team_mapping(self) -> Dict[str, List[str]]:
        """Retorna o mapeamento de times para usuários"""
        return {
            "Equipe Fenix": ["Paola Chagas"],
            "Equipe Bulls": ["Maria Eduarda "]
        }

    def get_target_users(self) -> List[str]:
        """Retorna a lista de usuários de interesse para comparação"""
        return ["Maria Eduarda ", "Paola Chagas"] 