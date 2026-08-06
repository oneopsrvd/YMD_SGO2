# YMD_SGO2 - Monitor YMS em Tempo Real (Pátio SGO2 - Rio Verde/GO)

Dashboard em tempo real para monitoramento do pátio do **Service Center Rio Verde - GO (SGO2)** do Mercado Livre.

## 🚀 Funcionalidades
- **Monitoramento em Tempo Real (Streaming)**: Consulta direta nas tabelas transacionais do BigQuery (`BT_YMS_JOURNEY_PLANNER`, `LK_SHP_LG_ROUTES`, `LK_PLACER_PLACES`, `LK_MLB_PLACES_AGENCY_LIST`, `LK_UR_CONFIG_XPT_VIRTUAL`).
- **Tabela de Prioridade #1 com Farol Operacional**:
  - **Último veículo que entrou fica na 1ª linha** (Ordenação por Check-in DESC).
  - 🟢 **Farol Verde**: Estadia <= 20 min.
  - 🟡 **Farol Amarelo**: Estadia entre 21 e 30 min.
  - 🔴 **Farol Vermelho**: Estadia > 30 min (Estouro de Meta).
- **Ranking de Carros Ofensores**: Classificação dos veículos que ultrapassaram a meta de 30 min (ordenados do maior tempo para o menor).
- **Indicador YMS do Dia**: Aderência global de permanência em % de todas as rotas operadas no dia.
- **Detecção Automática de XPT**: Identificação de operações de Cross-docking / Transferência / PUDO.
- **Filtros e CSV**: Filtro por placa, tipo de veículo, operações XPT e botão de exportação para CSV.
- **Auto-Refresh 60s**: Atualização contínua a cada minuto.

---

## 🛠️ Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Credenciais GCP autenticadas (`gcloud auth application-default login`) com acesso ao projeto `meli-bi-data`.

### Passos
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute a aplicação:
   ```bash
   streamlit run app_sgo2_realtime.py --server.port 8505
   ```
3. Ou execute com o gerador de Túnel HTTPS público:
   ```bash
   python run_dashboard_with_tunnel.py
   ```

---

## 🐳 Execução via Docker
```bash
docker build -t yms_sgo2_dashboard .
docker run -p 8080:8080 yms_sgo2_dashboard
```
