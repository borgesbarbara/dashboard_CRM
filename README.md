# Dashboard CRM - HOUSE

Dashboard para análise de funil de vendas integrado com RD Station CRM.

## 🚀 Deploy no Streamlit Cloud

### Pré-requisitos
- Conta no GitHub
- Conta no Streamlit Community Cloud

### Passos para Deploy

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/SEU_REPO.git
   cd SEU_REPO
   ```

2. **Configure as variáveis de ambiente no Streamlit Cloud:**
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Vá em "Secrets" da sua aplicação
   - Adicione:
   ```toml
   [secrets]
   API_BASE_URL = "https://crm.rdstation.com"
   API_TOKEN = "SUA_CHAVE_API_AQUI"
   ```

3. **Deploy:**
   - Repository: Seu repositório
   - Branch: `main`
   - Main file path: `app_refactored.py`
   - Clique em "Deploy!"

### 📁 Estrutura do Projeto

```
├── app_refactored.py          # Arquivo principal (entrypoint)
├── app.py                     # Versão completa do dashboard
├── frontend/                  # Componentes da interface
│   ├── components/           # Gráficos e filtros
│   ├── pages/               # Páginas do dashboard
│   └── utils/               # Utilitários da UI
├── backend/                  # Lógica de negócio
│   ├── api/                 # Cliente da API RD Station
│   ├── models/              # Modelos de dados
│   └── utils/               # Utilitários
├── requirements.txt          # Dependências Python
├── runtime.txt              # Versão do Python
└── .gitignore               # Arquivos ignorados pelo Git
```

### 🔧 Tecnologias

- **Frontend:** Streamlit
- **Backend:** Python
- **APIs:** RD Station CRM
- **Gráficos:** Plotly
- **Dados:** Pandas

### 📊 Funcionalidades

- Dashboard de funil de vendas
- Análise de etapas do CRM
- Gráficos interativos
- Filtros por período
- Auto-refresh a cada 5 minutos

### 🚨 Importante

- **NUNCA** faça commit do arquivo `.env`
- Use sempre o painel "Secrets" do Streamlit para variáveis sensíveis
- O arquivo principal para deploy é `app_refactored.py`

### 📞 Suporte

Para dúvidas sobre o deploy, consulte a [documentação do Streamlit](https://docs.streamlit.io/streamlit-community-cloud).
