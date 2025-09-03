"""
Modelos de dados para o sistema
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date


@dataclass
class Deal:
    """Modelo para representar um negócio"""
    id: str
    name: str
    rating: int
    stage_name: str
    user_name: Optional[str] = None
    pipeline_id: Optional[str] = None
    pipeline_name: Optional[str] = None


@dataclass
class Stage:
    """Modelo para representar uma etapa do funil"""
    id: str
    name: str
    nickname: Optional[str] = None
    order: Optional[int] = None
    pipeline_id: Optional[str] = None
    pipeline_name: Optional[str] = None
    objective: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Pipeline:
    """Modelo para representar um funil de vendas"""
    id: str
    name: str
    stages: Optional[List[Stage]] = None


@dataclass
class FunnelData:
    """Modelo para dados de funil processados"""
    stage: str
    count: int


@dataclass
class ComparativeData:
    """Modelo para dados comparativos por usuário"""
    user: str
    stage: str
    quantity: int


@dataclass
class APIConfig:
    """Modelo para configuração da API"""
    base_url: str
    token: str
    timeout: int = 30


@dataclass
class DateRange:
    """Modelo para intervalo de datas"""
    start_date: date
    end_date: date


@dataclass
class TeamMapping:
    """Modelo para mapeamento de times"""
    team_name: str
    users: List[str]


# Constantes
HOUSE_PIPELINE_ID = "689b59706e704a0024fc2374"
DEFAULT_STAGE_ORDER = [
    "LEADs", "LIGAÇÃO 1", "MENSAGEM", "LIGAÇÃO 2", "FOLLOW UP", 
    "AGENDAMENTO", "ATENDIMENTO REALIZADO", "NEGOCIAÇÃO", "FECHAMENTO", "PERDIDA"
]

# Usuários padrão (serão expandidos dinamicamente)
DEFAULT_TARGET_USERS = ["Maria Eduarda ", "Paola Chagas"]

# Mapeamento de times (será expandido dinamicamente)
DEFAULT_TEAM_MAPPINGS = {
    "Equipe Fenix": ["Paola Chagas"],
    "Equipe Bulls": ["Maria Eduarda "]
}

# Cores para usuários (será expandido dinamicamente)
DEFAULT_USER_COLORS = {
    "Maria Eduarda ": "lightcoral",
    "Paola Chagas": "lightblue"
} 