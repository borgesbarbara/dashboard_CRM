"""
Cliente para API do RD Station CRM
"""
import requests
import streamlit as st
from typing import Optional, Dict, List, Any


class RDStationClient:
    """Cliente para interagir com a API do RD Station CRM"""
    
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {"accept": "application/json"}
    
    @st.cache_data(ttl=300)
    def fetch_crm_data(_self, start_date: str, end_date: str) -> Optional[Dict]:
        """Busca dados do RD Station CRM"""
        try:
            url = f"{_self.base_url}/api/v1/deals"
            
            params = {
                "token": _self.token,
                "start_date": start_date,
                "end_date": end_date,
                "limit": 1000  # Aumentar de 100 para 1000 para dados completos
            }
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None

    @st.cache_data(ttl=300)
    def fetch_real_stages(_self) -> Optional[List]:
        """Busca as etapas reais dos funis de vendas"""
        try:
            url = f"{_self.base_url}/api/v1/deal_stages"
            params = {"token": _self.token}
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
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

    @st.cache_data(ttl=300)
    def fetch_pipeline_stages(_self) -> Optional[Dict]:
        """Busca funis e etapas do RD Station CRM"""
        try:
            url = f"{_self.base_url}/api/v1/deal_pipelines"
            
            # Tentar primeiro com Authorization header
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {_self.token}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            
            # Se falhou, tentar com token como parâmetro
            params = {"token": _self.token}
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None

    @st.cache_data(ttl=300)
    def fetch_stage_details(_self, stage_id: str) -> Optional[Dict]:
        """Busca detalhes de uma etapa específica"""
        try:
            url = f"{_self.base_url}/api/v1/deal_stages/{stage_id}"
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {_self.token}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None

    @st.cache_data(ttl=300)
    def fetch_team_pipelines(_self) -> Optional[List]:
        """Busca funis específicos das equipes Bulls e Fenix"""
        try:
            url = f"{_self.base_url}/api/v1/deal_pipelines"
            params = {"token": _self.token}
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
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

    @st.cache_data(ttl=30)
    def fetch_house_funnel_data(_self, start_date: str, end_date: str) -> Optional[Dict]:
        """Busca dados específicos do Funil - HOUSE"""
        try:
            url = f"{_self.base_url}/api/v1/deals"
            
            params = {
                "token": _self.token,
                "start_date": start_date,
                "end_date": end_date,
                "limit": 1000,  # Aumentar de 100 para 1000 para dados completos
                "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
            }
            
            print(f"🔍 DEBUG: Buscando deals do FUNIL HOUSE específico")
            print(f"🔍 DEBUG: URL: {url}")
            print(f"🔍 DEBUG: Params: {params}")
            print(f"🔍 DEBUG: Funil ID: 689b59706e704a0024fc2374 (HOUSE)")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"🔍 DEBUG: Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                deals_count = len(data.get('deals', []))
                print(f"🔍 DEBUG: Deals do FUNIL HOUSE encontrados: {deals_count}")
                
                # Verificar se os deals realmente pertencem ao funil HOUSE
                if deals_count > 0:
                    first_deal = data['deals'][0]
                    pipeline_info = first_deal.get('deal_pipeline', {})
                    pipeline_id = pipeline_info.get('id')
                    pipeline_name = pipeline_info.get('name', 'N/A')
                    print(f"🔍 DEBUG: Primeiro deal - Pipeline: {pipeline_name} (ID: {pipeline_id})")
                    print(f"🔍 DEBUG: Confirmação: Este deal pertence ao funil HOUSE? {'SIM' if pipeline_id == '689b59706e704a0024fc2374' else 'NÃO'}")
                
                return data
            else:
                print(f"🔍 DEBUG: Erro na requisição de deals HOUSE - Status: {response.status_code}")
                print(f"🔍 DEBUG: Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"🔍 DEBUG: Exception: {str(e)}")
            return None

    @st.cache_data(ttl=300)
    def fetch_house_funnel_stages(_self) -> Optional[List]:
        """Busca etapas específicas do Funil - HOUSE"""
        try:
            url = f"{_self.base_url}/api/v1/deal_stages"
            params = {
                "token": _self.token,
                "deal_pipeline_id": "689b59706e704a0024fc2374"  # ID do Funil - HOUSE
            }
            
            print(f"DEBUG: Buscando etapas do HOUSE em: {url}")
            print(f"DEBUG: Headers: {_self.headers}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
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

    @st.cache_data(ttl=30)
    def fetch_all_funnel_data(_self, start_date: str, end_date: str) -> Optional[Dict]:
        """Busca dados de todos os funis para comparar usuários"""
        try:
            url = f"{_self.base_url}/api/v1/deals"
            
            params = {
                "token": _self.token,
                "start_date": start_date,
                "end_date": end_date,
                "limit": 500  # Aumentar limite para pegar mais dados
            }
            
            print(f"🔍 DEBUG: Buscando TODOS os deals (SEM filtro de funil)")
            print(f"🔍 DEBUG: URL: {url}")
            print(f"🔍 DEBUG: Params: {params}")
            print(f"🔍 DEBUG: ⚠️  ATENÇÃO: Esta função busca deals de TODOS os funis, não apenas HOUSE!")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"🔍 DEBUG: Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                deals_count = len(data.get('deals', []))
                print(f"🔍 DEBUG: Total de deals encontrados (TODOS os funis): {deals_count}")
                
                # Verificar a distribuição dos deals por funil
                if deals_count > 0:
                    pipeline_counts = {}
                    for deal in data['deals'][:10]:  # Verificar apenas os primeiros 10
                        pipeline_info = deal.get('deal_pipeline', {})
                        pipeline_name = pipeline_info.get('name', 'Sem nome')
                        pipeline_counts[pipeline_name] = pipeline_counts.get(pipeline_name, 0) + 1
                    
                    print(f"🔍 DEBUG: Distribuição dos primeiros 10 deals por funil:")
                    for pipeline_name, count in pipeline_counts.items():
                        print(f"🔍 DEBUG:   - {pipeline_name}: {count} deals")
                
                return data
            else:
                print(f"🔍 DEBUG: Erro na requisição - Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"🔍 DEBUG: Exception: {str(e)}")
            return None

    @st.cache_data(ttl=300)
    def fetch_all_users(_self, start_date: str, end_date: str) -> Optional[List[str]]:
        """Descobre todos os usuários disponíveis no funil HOUSE"""
        try:
            # Buscar dados de todos os deals
            deals_data = _self.fetch_house_funnel_data(start_date, end_date)
            
            if not deals_data or "deals" not in deals_data:
                print(f"DEBUG: Nenhum dado de deals encontrado")
                return []
            
            deals = deals_data["deals"]
            print(f"DEBUG: Total de deals encontrados: {len(deals)}")
            
            users = set()
            
            # Extrair todos os usuários únicos
            for i, deal in enumerate(deals):
                if "user" in deal and deal["user"]:
                    user_info = deal["user"]
                    if isinstance(user_info, dict) and "name" in user_info:
                        user_name = user_info["name"].strip()
                        if user_name:  # Só adicionar se não for vazio
                            users.add(user_name)
                            print(f"DEBUG: Usuário {i+1}: '{user_name}'")
                    else:
                        print(f"DEBUG: Deal {i+1} - user_info inválido: {user_info}")
                else:
                    print(f"DEBUG: Deal {i+1} - sem usuário ou usuário vazio")
            
            # Ordenar usuários alfabeticamente
            sorted_users = sorted(list(users))
            print(f"DEBUG: Total de usuários únicos encontrados: {len(sorted_users)}")
            print(f"DEBUG: Lista completa de usuários: {sorted_users}")
            
            return sorted_users
            
        except Exception as e:
            print(f"DEBUG: Exception em fetch_all_users: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def fetch_house_users(_self, start_date: str, end_date: str) -> Optional[List[str]]:
        """Descobre todos os usuários do Funil - HOUSE"""
        try:
            # Buscar dados específicos do Funil - HOUSE
            deals_data = _self.fetch_house_funnel_data(start_date, end_date)
            
            if not deals_data or "deals" not in deals_data:
                print(f"DEBUG: Nenhum dado de deals do HOUSE encontrado")
                return []
            
            deals = deals_data["deals"]
            print(f"DEBUG: Total de deals do HOUSE encontrados: {len(deals)}")
            
            users = set()
            
            # Extrair todos os usuários únicos do HOUSE
            for i, deal in enumerate(deals):
                if "user" in deal and deal["user"]:
                    user_info = deal["user"]
                    if isinstance(user_info, dict) and "name" in user_info:
                        user_name = user_info["name"].strip()
                        if user_name:  # Só adicionar se não for vazio
                            users.add(user_name)
                            print(f"DEBUG: Usuário HOUSE {i+1}: '{user_name}'")
                    else:
                        print(f"DEBUG: Deal HOUSE {i+1} - user_info inválido: {user_info}")
                else:
                    print(f"DEBUG: Deal HOUSE {i+1} - sem usuário ou usuário vazio")
            
            # Ordenar usuários alfabeticamente
            sorted_users = sorted(list(users))
            print(f"DEBUG: Total de usuários únicos do HOUSE: {len(sorted_users)}")
            print(f"DEBUG: Lista completa de usuários do HOUSE: {sorted_users}")
            
            return sorted_users
            
        except Exception as e:
            print(f"DEBUG: Exception em fetch_house_users: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def fetch_team_users(_self, team_id: str) -> Optional[List[str]]:
        """Busca usuários de uma equipe específica"""
        try:
            url = f"{_self.base_url}/api/v1/teams/{team_id}/users"
            
            params = {
                "token": _self.token
            }
            
            print(f"DEBUG: Buscando usuários da equipe {team_id} em: {url}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                users = []
                
                # Verificar diferentes estruturas possíveis da resposta
                if isinstance(data, dict):
                    if "users" in data:
                        users_data = data["users"]
                        print(f"DEBUG: Encontrados {len(users_data)} usuários na chave 'users'")
                    elif "data" in data:
                        users_data = data["data"]
                        print(f"DEBUG: Encontrados {len(users_data)} usuários na chave 'data'")
                    else:
                        users_data = data
                        print(f"DEBUG: Usando dados diretos, chaves: {list(data.keys())}")
                elif isinstance(data, list):
                    users_data = data
                    print(f"DEBUG: Dados são uma lista com {len(data)} itens")
                else:
                    print(f"DEBUG: Tipo de dados inesperado: {type(data)}")
                    return []
                
                # Extrair nomes dos usuários
                for i, user in enumerate(users_data):
                    if isinstance(user, dict):
                        # Tentar diferentes campos possíveis para o nome
                        user_name = None
                        for field in ["name", "full_name", "display_name", "username"]:
                            if field in user and user[field]:
                                user_name = user[field].strip()
                                break
                        
                        if user_name:
                            users.append(user_name)
                            print(f"DEBUG: Usuário da equipe {i+1}: '{user_name}'")
                        else:
                            print(f"DEBUG: Usuário da equipe {i+1} - sem nome válido: {user}")
                    else:
                        print(f"DEBUG: Usuário da equipe {i+1} - formato inválido: {user}")
                
                # Ordenar usuários alfabeticamente
                sorted_users = sorted(list(set(users)))  # Remove duplicatas
                print(f"DEBUG: Total de usuários únicos da equipe {team_id}: {len(sorted_users)}")
                print(f"DEBUG: Lista completa de usuários da equipe: {sorted_users}")
                
                return sorted_users
            else:
                print(f"DEBUG: Erro na requisição - Status: {response.status_code}")
                print(f"DEBUG: Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_team_users: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def fetch_teams_directly(_self) -> Optional[Dict]:
        """Busca todas as equipes diretamente do endpoint /api/v1/teams"""
        try:
            url = f"{_self.base_url}/api/v1/teams"
            
            params = {
                "token": _self.token
            }
            
            print(f"DEBUG: Buscando equipes diretamente em: {url}")
            print(f"DEBUG: Params: {params}")
            print(f"DEBUG: Headers: {_self.headers}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"DEBUG: Status Code: {response.status_code}")
            print(f"DEBUG: Response Headers: {dict(response.headers)}")
            print(f"DEBUG: Response Text (primeiros 1000 chars): {response.text[:1000]}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Data type: {type(data)}")
                print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Verificar diferentes estruturas possíveis da resposta
                if isinstance(data, dict):
                    if "teams" in data:
                        teams_data = data["teams"]
                        print(f"DEBUG: Encontradas {len(teams_data)} equipes na chave 'teams'")
                    elif "data" in data:
                        teams_data = data["data"]
                        print(f"DEBUG: Encontradas {len(teams_data)} equipes na chave 'data'")
                    else:
                        teams_data = data
                        print(f"DEBUG: Usando dados diretos, chaves: {list(data.keys())}")
                elif isinstance(data, list):
                    teams_data = data
                    print(f"DEBUG: Dados são uma lista com {len(data)} itens")
                else:
                    print(f"DEBUG: Tipo de dados inesperado: {type(data)}")
                    return {}
                
                # Processar equipes
                teams_info = {}
                print(f"DEBUG: Iniciando processamento de {len(teams_data)} equipes")
                
                for i, team in enumerate(teams_data):
                    print(f"DEBUG: Processando equipe {i+1}: {team}")
                    
                    if isinstance(team, dict):
                        team_id = team.get("id", f"team_{i}")
                        team_name = team.get("name", f"Equipe {i+1}")
                        
                        print(f"DEBUG: Equipe {i+1} - ID: {team_id}, Nome: {team_name}")
                        
                        # Extrair usuários da equipe
                        users = []
                        if "team_users" in team:
                            print(f"DEBUG: Equipe {i+1} tem campo 'team_users': {team['team_users']}")
                            if isinstance(team["team_users"], list):
                                print(f"DEBUG: Equipe {i+1} tem {len(team['team_users'])} usuários na lista")
                                for j, user in enumerate(team["team_users"]):
                                    print(f"DEBUG: Processando usuário {j+1} da equipe {i+1}: {user}")
                                    if isinstance(user, dict):
                                        user_name = None
                                        for field in ["name", "full_name", "display_name", "username"]:
                                            if field in user and user[field]:
                                                user_name = user[field].strip()
                                                print(f"DEBUG: Usuário {j+1} - campo '{field}': '{user_name}'")
                                                break
                                        
                                        if user_name:
                                            users.append(user_name)
                                            print(f"DEBUG: Usuário {j+1} adicionado: '{user_name}'")
                                        else:
                                            print(f"DEBUG: Usuário {j+1} - sem nome válido: {user}")
                                    else:
                                        print(f"DEBUG: Usuário {j+1} - formato inválido: {user}")
                            else:
                                print(f"DEBUG: Equipe {i+1} - campo 'team_users' não é lista: {type(team['team_users'])}")
                        elif "users" in team:
                            print(f"DEBUG: Equipe {i+1} tem campo 'users': {team['users']}")
                            if isinstance(team["users"], list):
                                print(f"DEBUG: Equipe {i+1} tem {len(team['users'])} usuários na lista")
                                for j, user in enumerate(team["users"]):
                                    print(f"DEBUG: Processando usuário {j+1} da equipe {i+1}: {user}")
                                    if isinstance(user, dict):
                                        user_name = None
                                        for field in ["name", "full_name", "display_name", "username"]:
                                            if field in user and user[field]:
                                                user_name = user[field].strip()
                                                print(f"DEBUG: Usuário {j+1} - campo '{field}': '{user_name}'")
                                                break
                                        
                                        if user_name:
                                            users.append(user_name)
                                            print(f"DEBUG: Usuário {j+1} adicionado: '{user_name}'")
                                        else:
                                            print(f"DEBUG: Usuário {j+1} - sem nome válido: {user}")
                                    else:
                                        print(f"DEBUG: Usuário {j+1} - formato inválido: {user}")
                            else:
                                print(f"DEBUG: Equipe {i+1} - campo 'users' não é lista: {type(team['users'])}")
                        else:
                            print(f"DEBUG: Equipe {i+1} - sem campo 'team_users' ou 'users'")
                        
                        teams_info[team_name] = {
                            "id": team_id,
                            "name": team_name,
                            "users": users
                        }
                        
                        print(f"DEBUG: Equipe {i+1} finalizada: '{team_name}' (ID: {team_id}) - {len(users)} usuários")
                        for j, user in enumerate(users, 1):
                            print(f"  - Usuário {j}: '{user}'")
                    else:
                        print(f"DEBUG: Equipe {i+1} - formato inválido: {team}")
                
                print(f"DEBUG: Total de equipes processadas: {len(teams_info)}")
                print(f"DEBUG: Equipes encontradas: {list(teams_info.keys())}")
                
                # Verificar se há usuários
                total_users = sum(len(team_info['users']) for team_info in teams_info.values())
                print(f"DEBUG: Total de usuários em todas as equipes: {total_users}")
                
                return teams_info
            else:
                print(f"DEBUG: Erro na requisição - Status: {response.status_code}")
                print(f"DEBUG: Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_teams_directly: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {}

    @st.cache_data(ttl=300)
    def fetch_users_directly(_self) -> Optional[List[str]]:
        """Busca todos os usuários diretamente do endpoint /api/v1/users"""
        try:
            url = f"{_self.base_url}/api/v1/users"
            
            params = {
                "token": _self.token
            }
            
            print(f"DEBUG: Buscando usuários diretamente em: {url}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"DEBUG: Status Code: {response.status_code}")
            print(f"DEBUG: Response Text (primeiros 500 chars): {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                users = []
                
                # Verificar diferentes estruturas possíveis da resposta
                if isinstance(data, dict):
                    if "users" in data:
                        users_data = data["users"]
                        print(f"DEBUG: Encontrados {len(users_data)} usuários na chave 'users'")
                    elif "data" in data:
                        users_data = data["data"]
                        print(f"DEBUG: Encontrados {len(users_data)} usuários na chave 'data'")
                    else:
                        users_data = data
                        print(f"DEBUG: Usando dados diretos, chaves: {list(data.keys())}")
                elif isinstance(data, list):
                    users_data = data
                    print(f"DEBUG: Dados são uma lista com {len(data)} itens")
                else:
                    print(f"DEBUG: Tipo de dados inesperado: {type(data)}")
                    return []
                
                # Extrair nomes dos usuários
                for i, user in enumerate(users_data):
                    if isinstance(user, dict):
                        # Tentar diferentes campos possíveis para o nome
                        user_name = None
                        for field in ["name", "full_name", "display_name", "username"]:
                            if field in user and user[field]:
                                user_name = user[field].strip()
                                break
                        
                        if user_name:
                            users.append(user_name)
                            print(f"DEBUG: Usuário {i+1}: '{user_name}'")
                        else:
                            print(f"DEBUG: Usuário {i+1} - sem nome válido: {user}")
                    else:
                        print(f"DEBUG: Usuário {i+1} - formato inválido: {user}")
                
                # Ordenar usuários alfabeticamente
                sorted_users = sorted(list(set(users)))  # Remove duplicatas
                print(f"DEBUG: Total de usuários únicos encontrados: {len(sorted_users)}")
                print(f"DEBUG: Lista completa de usuários: {sorted_users}")
                
                return sorted_users
            else:
                print(f"DEBUG: Erro na requisição - Status: {response.status_code}")
                print(f"DEBUG: Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_users_directly: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def fetch_all_users_no_date_limit(_self) -> Optional[List[str]]:
        """Descobre todos os usuários disponíveis no funil sem limite de data"""
        try:
            url = f"{_self.base_url}/api/v1/deals"
            
            params = {
                "token": _self.token,
                "limit": 1000  # Limite máximo para pegar todos os dados
            }
            
            print(f"DEBUG: Buscando TODOS os deals sem limite de data em: {url}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"DEBUG: Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('deals', [])
                print(f"DEBUG: Total de deals encontrados (sem limite de data): {len(deals)}")
                
                users = set()
                
                # Extrair todos os usuários únicos
                for i, deal in enumerate(deals):
                    if "user" in deal and deal["user"]:
                        user_info = deal["user"]
                        if isinstance(user_info, dict) and "name" in user_info:
                            user_name = user_info["name"].strip()
                            if user_name:  # Só adicionar se não for vazio
                                users.add(user_name)
                                print(f"DEBUG: Usuário {i+1} (sem data): '{user_name}'")
                        else:
                            print(f"DEBUG: Deal {i+1} (sem data) - user_info inválido: {user_info}")
                    else:
                        print(f"DEBUG: Deal {i+1} (sem data) - sem usuário ou usuário vazio")
                
                # Ordenar usuários alfabeticamente
                sorted_users = sorted(list(users))
                print(f"DEBUG: Total de usuários únicos (sem data): {len(sorted_users)}")
                print(f"DEBUG: Lista completa de usuários (sem data): {sorted_users}")
                
                return sorted_users
            else:
                print(f"DEBUG: Erro na requisição (sem data) - Status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_all_users_no_date_limit: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def fetch_house_users_no_date_limit(_self) -> List[str]:
        """Busca usuários do funil HOUSE sem limite de data"""
        try:
            print(f"DEBUG: Iniciando busca de usuários HOUSE sem limite de data")
            
            # Buscar todos os deals do funil HOUSE usando pipeline_name
            url = f"{_self.base_url}/api/v1/deals"
            params = {
                "token": _self.token,
                "limit": 1000,  # Aumentar limite para pegar mais deals
                "pipeline_name": "HOUSE"  # Usar pipeline_name em vez de deal_pipeline_id
            }
            
            print(f"DEBUG: URL para deals HOUSE: {url}")
            print(f"DEBUG: Params para deals HOUSE: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            print(f"DEBUG: Status Code para deals HOUSE: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Tipo de dados HOUSE: {type(data)}")
                print(f"DEBUG: Chaves dos dados HOUSE: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extrair deals
                if isinstance(data, dict):
                    deals = data.get("deals", [])
                    total_deals = data.get("total", 0)
                    has_more = data.get("has_more", False)
                    print(f"DEBUG: Total de deals na resposta: {total_deals}")
                    print(f"DEBUG: Has more deals: {has_more}")
                elif isinstance(data, list):
                    deals = data
                    total_deals = len(deals)
                    has_more = False
                else:
                    deals = []
                    total_deals = 0
                    has_more = False
                
                print(f"DEBUG: Total de deals HOUSE encontrados: {len(deals)}")
                
                # Se há mais deals, buscar mais páginas
                if has_more and len(deals) < total_deals:
                    print(f"DEBUG: Há mais deals disponíveis. Buscando páginas adicionais...")
                    all_deals = deals.copy()
                    
                    # Buscar páginas adicionais
                    page = 1
                    while has_more and len(all_deals) < total_deals:
                        page += 1
                        params["page"] = page
                        print(f"DEBUG: Buscando página {page}...")
                        
                        response = requests.get(url, headers=_self.headers, params=params, timeout=30)
                        if response.status_code == 200:
                            page_data = response.json()
                            if isinstance(page_data, dict):
                                page_deals = page_data.get("deals", [])
                                all_deals.extend(page_deals)
                                has_more = page_data.get("has_more", False)
                                print(f"DEBUG: Página {page}: {len(page_deals)} deals adicionados")
                            else:
                                break
                        else:
                            print(f"DEBUG: Erro ao buscar página {page}: {response.status_code}")
                            break
                    
                    deals = all_deals
                    print(f"DEBUG: Total final de deals HOUSE após todas as páginas: {len(deals)}")
                
                # Extrair usuários únicos
                users = set()
                deals_without_users = 0
                deals_with_users = 0
                deals_by_user = {}  # Contar deals por usuário
                
                for i, deal in enumerate(deals):
                    print(f"DEBUG: Processando deal HOUSE {i+1}: {deal.get('id', 'sem_id')}")
                    print(f"DEBUG: Deal {i+1} - Nome: {deal.get('name', 'sem_nome')}")
                    
                    # Verificar diferentes campos onde o usuário pode estar
                    user_name = None
                    
                    # Campo 'owner'
                    if "owner" in deal and deal["owner"]:
                        owner = deal["owner"]
                        print(f"DEBUG: Deal {i+1} tem owner: {owner}")
                        if isinstance(owner, dict):
                            for field in ["name", "full_name", "display_name", "username"]:
                                if field in owner and owner[field]:
                                    user_name = owner[field].strip()
                                    print(f"DEBUG: Deal {i+1} - owner campo '{field}': '{user_name}'")
                                    break
                        elif isinstance(owner, str):
                            user_name = owner.strip()
                            print(f"DEBUG: Deal {i+1} - owner string: '{user_name}'")
                    
                    # Campo 'user'
                    elif "user" in deal and deal["user"]:
                        user = deal["user"]
                        print(f"DEBUG: Deal {i+1} tem user: {user}")
                        if isinstance(user, dict):
                            for field in ["name", "full_name", "display_name", "username"]:
                                if field in user and user[field]:
                                    user_name = user[field].strip()
                                    print(f"DEBUG: Deal {i+1} - user campo '{field}': '{user_name}'")
                                    break
                        elif isinstance(user, str):
                            user_name = user.strip()
                            print(f"DEBUG: Deal {i+1} - user string: '{user_name}'")
                    
                    # Campo 'assigned_user'
                    elif "assigned_user" in deal and deal["assigned_user"]:
                        assigned_user = deal["assigned_user"]
                        print(f"DEBUG: Deal {i+1} tem assigned_user: {assigned_user}")
                        if isinstance(assigned_user, dict):
                            for field in ["name", "full_name", "display_name", "username"]:
                                if field in assigned_user and assigned_user[field]:
                                    user_name = assigned_user[field].strip()
                                    print(f"DEBUG: Deal {i+1} - assigned_user campo '{field}': '{user_name}'")
                                    break
                        elif isinstance(assigned_user, str):
                            user_name = assigned_user.strip()
                            print(f"DEBUG: Deal {i+1} - assigned_user string: '{user_name}'")
                    
                    # Verificar se encontrou usuário
                    if user_name:
                        users.add(user_name)
                        deals_with_users += 1
                        deals_by_user[user_name] = deals_by_user.get(user_name, 0) + 1
                        print(f"DEBUG: Deal {i+1} - usuário adicionado: '{user_name}'")
                    else:
                        deals_without_users += 1
                        print(f"DEBUG: Deal {i+1} - SEM usuário encontrado")
                        print(f"DEBUG: Deal {i+1} - campos disponíveis: {list(deal.keys())}")
                        # Mostrar alguns campos para debug
                        for key in ["owner", "user", "assigned_user", "name", "title", "status"]:
                            if key in deal:
                                print(f"DEBUG: Deal {i+1} - campo '{key}': {deal[key]}")
                
                print(f"DEBUG: Resumo HOUSE:")
                print(f"  - Total de deals: {len(deals)}")
                print(f"  - Deals com usuários: {deals_with_users}")
                print(f"  - Deals sem usuários: {deals_without_users}")
                print(f"  - Usuários únicos encontrados: {len(users)}")
                print(f"  - Lista de usuários HOUSE: {sorted(list(users))}")
                print(f"  - Deals por usuário:")
                for user, count in sorted(deals_by_user.items()):
                    print(f"    - {user}: {count} deals")
                
                return sorted(list(users))
            else:
                print(f"DEBUG: Erro na requisição HOUSE - Status: {response.status_code}")
                print(f"DEBUG: Response HOUSE: {response.text}")
                return []
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_house_users_no_date_limit: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return []

    def test_all_house_endpoints(_self) -> Dict[str, Any]:
        """Testa todos os endpoints possíveis relacionados ao funil HOUSE"""
        try:
            print(f"DEBUG: Iniciando teste de todos os endpoints HOUSE")
            
            results = {}
            
            # 1. Testar endpoint de deals com diferentes parâmetros
            deals_tests = [
                {
                    "name": "deals_house_pipeline",
                    "url": f"{_self.base_url}/api/v1/deals",
                    "params": {
                        "token": _self.token,
                        "deal_pipeline_id": "689b59706e704a0024fc2374"
                    }
                },
                {
                    "name": "deals_house_stage",
                    "url": f"{_self.base_url}/api/v1/deals",
                    "params": {
                        "token": _self.token,
                        "deal_stage_id": "689b59706e704a0024fc2374"
                    }
                },
                {
                    "name": "deals_house_name",
                    "url": f"{_self.base_url}/api/v1/deals",
                    "params": {
                        "token": _self.token,
                        "pipeline_name": "HOUSE"
                    }
                },
                {
                    "name": "deals_all",
                    "url": f"{_self.base_url}/api/v1/deals",
                    "params": {
                        "token": _self.token,
                        "limit": 1000  # Aumentar de 100 para 1000 para dados completos
                    }
                }
            ]
            
            for test in deals_tests:
                print(f"DEBUG: Testando {test['name']}...")
                try:
                    response = requests.get(test["url"], headers=_self.headers, params=test["params"], timeout=10)
                    results[test["name"]] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "total_deals": 0,
                        "users_found": []
                    }
                    
                    if response.status_code == 200:
                        data = response.json()
                        deals = data.get("deals", [])
                        results[test["name"]]["total_deals"] = len(deals)
                        
                        # Extrair usuários
                        users = set()
                        for deal in deals:
                            for field in ["owner", "user", "assigned_user"]:
                                if field in deal and deal[field]:
                                    user_info = deal[field]
                                    if isinstance(user_info, dict):
                                        for name_field in ["name", "full_name", "display_name"]:
                                            if name_field in user_info and user_info[name_field]:
                                                users.add(user_info[name_field].strip())
                                                break
                                    elif isinstance(user_info, str):
                                        users.add(user_info.strip())
                                    break
                        
                        results[test["name"]]["users_found"] = sorted(list(users))
                        print(f"DEBUG: {test['name']} - {len(deals)} deals, {len(users)} usuários")
                    
                except Exception as e:
                    results[test["name"]] = {
                        "status_code": 0,
                        "success": False,
                        "error": str(e),
                        "total_deals": 0,
                        "users_found": []
                    }
                    print(f"DEBUG: Erro em {test['name']}: {str(e)}")
            
            # 2. Testar endpoint de stages do funil HOUSE
            stages_tests = [
                {
                    "name": "stages_house",
                    "url": f"{_self.base_url}/api/v1/deal_stages",
                    "params": {
                        "token": _self.token,
                        "deal_pipeline_id": "689b59706e704a0024fc2374"
                    }
                },
                {
                    "name": "stages_all",
                    "url": f"{_self.base_url}/api/v1/deal_stages",
                    "params": {
                        "token": _self.token
                    }
                }
            ]
            
            for test in stages_tests:
                print(f"DEBUG: Testando {test['name']}...")
                try:
                    response = requests.get(test["url"], headers=_self.headers, params=test["params"], timeout=10)
                    results[test["name"]] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "stages_found": []
                    }
                    
                    if response.status_code == 200:
                        data = response.json()
                        stages = data.get("deal_stages", [])
                        stage_names = [stage.get("name", "") for stage in stages if stage.get("name")]
                        results[test["name"]]["stages_found"] = stage_names
                        print(f"DEBUG: {test['name']} - {len(stages)} stages encontrados")
                    
                except Exception as e:
                    results[test["name"]] = {
                        "status_code": 0,
                        "success": False,
                        "error": str(e),
                        "stages_found": []
                    }
                    print(f"DEBUG: Erro em {test['name']}: {str(e)}")
            
            # 3. Testar endpoint de pipelines
            pipeline_tests = [
                {
                    "name": "pipelines_all",
                    "url": f"{_self.base_url}/api/v1/deal_pipelines",
                    "params": {
                        "token": _self.token
                    }
                }
            ]
            
            for test in pipeline_tests:
                print(f"DEBUG: Testando {test['name']}...")
                try:
                    response = requests.get(test["url"], headers=_self.headers, params=test["params"], timeout=10)
                    results[test["name"]] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "pipelines_found": []
                    }
                    
                    if response.status_code == 200:
                        data = response.json()
                        pipelines = data if isinstance(data, list) else data.get("deal_pipelines", [])
                        pipeline_names = [pipeline.get("name", "") for pipeline in pipelines if pipeline.get("name")]
                        results[test["name"]]["pipelines_found"] = pipeline_names
                        print(f"DEBUG: {test['name']} - {len(pipelines)} pipelines encontrados")
                    
                except Exception as e:
                    results[test["name"]] = {
                        "status_code": 0,
                        "success": False,
                        "error": str(e),
                        "pipelines_found": []
                    }
                    print(f"DEBUG: Erro em {test['name']}: {str(e)}")
            
            # 4. Testar endpoint de usuários
            users_tests = [
                {
                    "name": "users_all",
                    "url": f"{_self.base_url}/api/v1/users",
                    "params": {
                        "token": _self.token
                    }
                }
            ]
            
            for test in users_tests:
                print(f"DEBUG: Testando {test['name']}...")
                try:
                    response = requests.get(test["url"], headers=_self.headers, params=test["params"], timeout=10)
                    results[test["name"]] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "users_found": []
                    }
                    
                    if response.status_code == 200:
                        data = response.json()
                        users = data.get("users", []) if isinstance(data, dict) else data
                        user_names = []
                        for user in users:
                            if isinstance(user, dict):
                                for name_field in ["name", "full_name", "display_name"]:
                                    if name_field in user and user[name_field]:
                                        user_names.append(user[name_field].strip())
                                        break
                        results[test["name"]]["users_found"] = user_names
                        print(f"DEBUG: {test['name']} - {len(users)} usuários encontrados")
                    
                except Exception as e:
                    results[test["name"]] = {
                        "status_code": 0,
                        "success": False,
                        "error": str(e),
                        "users_found": []
                    }
                    print(f"DEBUG: Erro em {test['name']}: {str(e)}")
            
            print(f"DEBUG: Resumo dos testes:")
            for test_name, result in results.items():
                print(f"  - {test_name}: {'✅' if result['success'] else '❌'} (Status: {result['status_code']})")
            
            return results
            
        except Exception as e:
            print(f"DEBUG: Exception em test_all_house_endpoints: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {}

    def fetch_house_users_comprehensive(_self) -> Dict[str, Any]:
        """Busca usuários do funil HOUSE de forma mais abrangente"""
        try:
            print(f"DEBUG: Iniciando busca abrangente de usuários HOUSE")
            
            # 1. Buscar deals do funil HOUSE
            deals_url = f"{_self.base_url}/api/v1/deals"
            deals_params = {
                "token": _self.token,
                "limit": 1000,
                "deal_pipeline_id": "689b59706e704a0024fc2374"
            }
            
            print(f"DEBUG: Buscando deals do HOUSE...")
            deals_response = requests.get(deals_url, headers=_self.headers, params=deals_params, timeout=30)
            
            deals_users = set()
            if deals_response.status_code == 200:
                deals_data = deals_response.json()
                deals = deals_data.get("deals", [])
                print(f"DEBUG: Deals do HOUSE encontrados: {len(deals)}")
                
                for deal in deals:
                    # Extrair usuário do deal
                    user_name = None
                    for field in ["owner", "user", "assigned_user"]:
                        if field in deal and deal[field]:
                            user_info = deal[field]
                            if isinstance(user_info, dict):
                                for name_field in ["name", "full_name", "display_name"]:
                                    if name_field in user_info and user_info[name_field]:
                                        user_name = user_info[name_field].strip()
                                        break
                            elif isinstance(user_info, str):
                                user_name = user_info.strip()
                            if user_name:
                                break
                    
                    if user_name:
                        deals_users.add(user_name)
            
            print(f"DEBUG: Usuários encontrados via deals: {sorted(list(deals_users))}")
            
            # 2. Buscar todos os usuários da API
            users_url = f"{_self.base_url}/api/v1/users"
            users_params = {"token": _self.token}
            
            print(f"DEBUG: Buscando todos os usuários...")
            users_response = requests.get(users_url, headers=_self.headers, params=users_params, timeout=30)
            
            all_users = []
            if users_response.status_code == 200:
                users_data = users_response.json()
                if isinstance(users_data, dict) and "users" in users_data:
                    all_users = users_data["users"]
                elif isinstance(users_data, list):
                    all_users = users_data
                
                print(f"DEBUG: Total de usuários na API: {len(all_users)}")
            
            # 3. Buscar equipes para ver se há usuários associados ao HOUSE
            teams_url = f"{_self.base_url}/api/v1/teams"
            teams_params = {"token": _self.token}
            
            print(f"DEBUG: Buscando equipes...")
            teams_response = requests.get(teams_url, headers=_self.headers, params=teams_params, timeout=30)
            
            teams_users = set()
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                teams = teams_data.get("teams", [])
                print(f"DEBUG: Equipes encontradas: {len(teams)}")
                
                for team in teams:
                    team_name = team.get("name", "")
                    print(f"DEBUG: Verificando equipe: {team_name}")
                    
                    # Verificar se a equipe tem relação com HOUSE
                    if "house" in team_name.lower():
                        print(f"DEBUG: Equipe relacionada ao HOUSE encontrada: {team_name}")
                        if "team_users" in team:
                            for user in team["team_users"]:
                                if isinstance(user, dict) and "name" in user:
                                    teams_users.add(user["name"].strip())
                                    print(f"DEBUG: Usuário da equipe HOUSE: {user['name']}")
            
            print(f"DEBUG: Usuários encontrados via equipes HOUSE: {sorted(list(teams_users))}")
            
            # 4. Comparar e analisar
            all_users_names = set()
            for user in all_users:
                if isinstance(user, dict):
                    for field in ["name", "full_name", "display_name"]:
                        if field in user and user[field]:
                            all_users_names.add(user[field].strip())
                            break
            
            print(f"DEBUG: Todos os usuários da API: {sorted(list(all_users_names))}")
            
            # 5. Análise final
            house_users_via_deals = sorted(list(deals_users))
            house_users_via_teams = sorted(list(teams_users))
            all_users_list = sorted(list(all_users_names))
            
            # Usuários que estão na API mas não aparecem nos deals do HOUSE
            missing_users = [user for user in all_users_list if user not in house_users_via_deals]
            
            print(f"DEBUG: Análise final:")
            print(f"  - Usuários via deals HOUSE: {house_users_via_deals}")
            print(f"  - Usuários via equipes HOUSE: {house_users_via_teams}")
            print(f"  - Todos os usuários: {all_users_list}")
            print(f"  - Usuários que não aparecem nos deals HOUSE: {missing_users}")
            
            return {
                "house_users_via_deals": house_users_via_deals,
                "house_users_via_teams": house_users_via_teams,
                "all_users": all_users_list,
                "missing_users": missing_users,
                "total_deals": len(deals) if deals_response.status_code == 200 else 0,
                "total_users": len(all_users_list),
                "total_teams": len(teams) if teams_response.status_code == 200 else 0
            }
            
        except Exception as e:
            print(f"DEBUG: Exception em fetch_house_users_comprehensive: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {}

    def fetch_all_pipelines(_self) -> Dict[str, Any]:
        """Busca todos os funis disponíveis para verificar IDs"""
        try:
            url = f"{_self.base_url}/api/v1/deal_pipelines"
            params = {"token": _self.token}
            
            print(f"DEBUG: Buscando todos os funis em: {url}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=10)
            
            print(f"DEBUG: Status Code para funis: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Tipo de dados funis: {type(data)}")
                print(f"DEBUG: Chaves dos dados funis: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extrair funis
                if isinstance(data, dict):
                    pipelines = data.get("deal_pipelines", [])
                elif isinstance(data, list):
                    pipelines = data
                else:
                    pipelines = []
                
                print(f"DEBUG: Total de funis encontrados: {len(pipelines)}")
                
                # Processar cada funil
                pipelines_info = {}
                for i, pipeline in enumerate(pipelines):
                    if isinstance(pipeline, dict):
                        pipeline_id = pipeline.get("id", f"pipeline_{i}")
                        pipeline_name = pipeline.get("name", f"Funnel {i+1}")
                        
                        print(f"DEBUG: Funil {i+1}: '{pipeline_name}' (ID: {pipeline_id})")
                        
                        pipelines_info[pipeline_name] = {
                            "id": pipeline_id,
                            "name": pipeline_name,
                            "raw_data": pipeline
                        }
                
                print(f"DEBUG: Funis processados: {list(pipelines_info.keys())}")
                
                return {
                    "success": True,
                    "pipelines": pipelines_info,
                    "total": len(pipelines)
                }
            else:
                print(f"DEBUG: Erro na requisição de funis - Status: {response.status_code}")
                print(f"DEBUG: Response funis: {response.text}")
                return {
                    "success": False,
                    "error": f"Status {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            print(f"DEBUG: Exception em fetch_all_pipelines: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_teams_connectivity(self) -> Dict[str, Any]:
        """Testa a conectividade com o endpoint de equipes"""
        try:
            url = f"{self.base_url}/api/v1/teams"
            params = {"token": self.token}
            
            print(f"DEBUG: Testando conectividade com equipes em: {url}")
            print(f"DEBUG: Params: {params}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_text": response.text[:500] if response.text else "",
                "url": url,
                "headers": dict(response.headers)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": f"{self.base_url}/api/v1/teams"
            }

    def test_connectivity(self) -> Dict[str, Any]:
        """Testa a conectividade com a API"""
        try:
            url = f"{self.base_url}/api/v1/deal_stages"
            params = {"token": self.token}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_text": response.text[:200] if response.text else "",
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": f"{self.base_url}/api/v1/deal_stages"
            } 

    @st.cache_data(ttl=300)
    def investigate_paola_chagas_data(_self) -> Dict:
        """Investiga especificamente os dados da Paola Chagas para comparar com o CRM"""
        try:
            print(f"DEBUG: 🔍 Iniciando investigação específica da Paola Chagas")
            
            results = {
                "paola_deals": [],
                "paola_house_deals": [],
                "paola_all_deals": [],
                "paola_team_info": {},
                "comparison": {}
            }
            
            # 1. Buscar deals específicos da Paola Chagas
            print(f"DEBUG: 1. Buscando deals específicos da Paola Chagas...")
            
            # Buscar todos os deals
            url = f"{_self.base_url}/api/v1/deals"
            params = {
                "token": _self.token,
                "limit": 1000
            }
            
            response = requests.get(url, headers=_self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                all_deals = data.get("deals", [])
                
                # Filtrar deals da Paola
                paola_deals = []
                for deal in all_deals:
                    user_name = None
                    
                    # Verificar campo 'user'
                    if "user" in deal and deal["user"]:
                        user_info = deal["user"]
                        if isinstance(user_info, dict) and "name" in user_info:
                            user_name = user_info["name"].strip()
                        elif isinstance(user_info, str):
                            user_name = user_info.strip()
                    
                    # Verificar campo 'owner'
                    elif "owner" in deal and deal["owner"]:
                        owner = deal["owner"]
                        if isinstance(owner, dict) and "name" in owner:
                            user_name = owner["name"].strip()
                        elif isinstance(owner, str):
                            user_name = owner.strip()
                    
                    # Se é a Paola, adicionar ao resultado
                    if user_name and "paola" in user_name.lower():
                        paola_deals.append({
                            "id": deal.get("id"),
                            "name": deal.get("name"),
                            "user": user_name,
                            "pipeline": deal.get("deal_pipeline", {}).get("name"),
                            "stage": deal.get("deal_stage", {}).get("name"),
                            "status": deal.get("status"),
                            "rating": deal.get("rating"),
                            "created_at": deal.get("created_at"),
                            "updated_at": deal.get("updated_at")
                        })
                
                results["paola_all_deals"] = paola_deals
                print(f"DEBUG: Encontrados {len(paola_deals)} deals da Paola Chagas")
                
                # Mostrar detalhes de cada deal
                for i, deal in enumerate(paola_deals):
                    print(f"DEBUG: Deal {i+1} da Paola:")
                    print(f"  - ID: {deal['id']}")
                    print(f"  - Nome: {deal['name']}")
                    print(f"  - Pipeline: {deal['pipeline']}")
                    print(f"  - Stage: {deal['stage']}")
                    print(f"  - Status: {deal['status']}")
                    print(f"  - Rating: {deal['rating']}")
            
            # 2. Buscar deals do funil HOUSE da Paola
            print(f"DEBUG: 2. Buscando deals do funil HOUSE da Paola...")
            
            params_house = {
                "token": _self.token,
                "limit": 1000,
                "pipeline_name": "HOUSE"
            }
            
            response_house = requests.get(url, headers=_self.headers, params=params_house, timeout=30)
            
            if response_house.status_code == 200:
                data_house = response_house.json()
                house_deals = data_house.get("deals", [])
                
                # Filtrar deals da Paola no HOUSE
                paola_house_deals = []
                for deal in house_deals:
                    user_name = None
                    
                    if "user" in deal and deal["user"]:
                        user_info = deal["user"]
                        if isinstance(user_info, dict) and "name" in user_info:
                            user_name = user_info["name"].strip()
                        elif isinstance(user_info, str):
                            user_name = user_info.strip()
                    
                    elif "owner" in deal and deal["owner"]:
                        owner = deal["owner"]
                        if isinstance(owner, dict) and "name" in owner:
                            user_name = owner["name"].strip()
                        elif isinstance(owner, str):
                            user_name = owner.strip()
                    
                    if user_name and "paola" in user_name.lower():
                        paola_house_deals.append({
                            "id": deal.get("id"),
                            "name": deal.get("name"),
                            "user": user_name,
                            "pipeline": deal.get("deal_pipeline", {}).get("name"),
                            "stage": deal.get("deal_stage", {}).get("name"),
                            "status": deal.get("status"),
                            "rating": deal.get("rating")
                        })
                
                results["paola_house_deals"] = paola_house_deals
                print(f"DEBUG: Encontrados {len(paola_house_deals)} deals da Paola no funil HOUSE")
            
            # 3. Buscar informações da equipe da Paola
            print(f"DEBUG: 3. Buscando informações da equipe da Paola...")
            
            teams_url = f"{_self.base_url}/api/v1/teams"
            teams_params = {"token": _self.token}
            
            teams_response = requests.get(teams_url, headers=_self.headers, params=teams_params, timeout=30)
            
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                teams = teams_data.get("teams", [])
                
                for team in teams:
                    if "team_users" in team:
                        for user in team["team_users"]:
                            if "paola" in user.get("name", "").lower():
                                results["paola_team_info"] = {
                                    "team_name": team.get("name"),
                                    "team_id": team.get("id"),
                                    "user_name": user.get("name"),
                                    "user_email": user.get("email"),
                                    "user_id": user.get("id")
                                }
                                print(f"DEBUG: Paola encontrada na equipe: {team.get('name')}")
                                break
            
            # 4. Comparação e análise
            print(f"DEBUG: 4. Análise comparativa...")
            
            results["comparison"] = {
                "total_deals": len(results["paola_all_deals"]),
                "house_deals": len(results["paola_house_deals"]),
                "other_deals": len(results["paola_all_deals"]) - len(results["paola_house_deals"]),
                "team_info": results["paola_team_info"],
                "possible_issues": []
            }
            
            # Identificar possíveis problemas
            if len(results["paola_house_deals"]) == 0:
                results["comparison"]["possible_issues"].append("Nenhum deal da Paola encontrado no funil HOUSE")
            
            if len(results["paola_all_deals"]) == 0:
                results["comparison"]["possible_issues"].append("Nenhum deal da Paola encontrado na API")
            
            # Verificar se há deals em outros funis
            other_pipelines = set()
            for deal in results["paola_all_deals"]:
                if deal["pipeline"] and deal["pipeline"] != "HOUSE":
                    other_pipelines.add(deal["pipeline"])
            
            if other_pipelines:
                results["comparison"]["other_pipelines"] = list(other_pipelines)
                results["comparison"]["possible_issues"].append(f"Deals encontrados em outros funis: {list(other_pipelines)}")
            
            print(f"DEBUG: 🔍 Investigação da Paola Chagas concluída")
            print(f"DEBUG: Resumo:")
            print(f"  - Total de deals: {results['comparison']['total_deals']}")
            print(f"  - Deals no HOUSE: {results['comparison']['house_deals']}")
            print(f"  - Deals em outros funis: {results['comparison']['other_deals']}")
            print(f"  - Equipe: {results['comparison']['team_info'].get('team_name', 'N/A')}")
            print(f"  - Possíveis problemas: {results['comparison']['possible_issues']}")
            
            return results
            
        except Exception as e:
            print(f"DEBUG: Erro na investigação da Paola Chagas: {str(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return {"error": str(e)} 