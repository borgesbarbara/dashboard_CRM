
# Relatórios – RD Conversas (Streamlit)

App em Streamlit para consultar endpoints de **reports** da API Tallos/RD Station Conversas.

## Uso
1. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `.env`:
   ```env
   API_BASE_URL=https://api.tallos.com.br
   API_TOKEN=SEU_TOKEN_AQUI
   API_ENDPOINT=/megasac-api/v2/reports/messages  # ajuste para o endpoint real
   API_PARAMS={"team_id":123}                      # (opcional) parâmetros extras
   ```

3. Rode:
   ```bash
   streamlit run app.py
   ```

4. Na sidebar, ajuste Base URL, Token, Endpoint e Período. Parâmetros extras podem ser enviados como **JSON**.
