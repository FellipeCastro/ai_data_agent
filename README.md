# AI Data Agent

Agente de dados multi-agente construído com **LangGraph** e **LangChain**, capaz de interpretar perguntas em linguagem natural e decidir automaticamente se deve:

- consultar um banco **PostgreSQL** gerando e executando SQL (**SQL Analyst**), ou
- executar operações de **ETL** (extração de APIs e transformação com Pandas) (**ETL Analyst**).

Um nó roteador (LLM) classifica a pergunta do usuário e encaminha o fluxo para o subagente apropriado.

## Arquitetura

```
                 ┌───────────────┐
   pergunta ───▶ │  router_node  │
                 └───────┬───────┘
                         │ classifica: "sql" | "etl"
              ┌──────────┴──────────┐
              ▼                     ▼
      ┌───────────────┐     ┌───────────────┐
      │   sql_node     │     │   etl_node    │
      │ (sql_analyst)  │     │ (etl_analyst) │
      └───────────────┘     └───────────────┘
```

### Data Agent (`agents/data_agent.py`)
Grafo principal. Usa `RouterSchema` para classificar a mensagem do usuário como `sql` ou `etl` e delega para o subagente correspondente.

### SQL Analyst (`agents/sql_analyst.py`)
Pipeline com várias etapas até responder a pergunta:
1. **curate_ques** — reescreve/curadoria da pergunta do usuário.
2. **prompt_query_context** — busca o schema do banco (tabelas, colunas, tipos e amostra de dados) via `utils/database.py` e monta o prompt.
3. **generate_sql** — gera a query SQL (Postgres) via LLM.
4. **is_safe_sql** — um LLM "juiz" valida se a query é somente leitura (bloqueia `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, etc.).
5. **execute_sql** / **canceled_sql** — executa a query se for segura, ou cancela e explica o motivo.
6. **represent_final_answer** — traduz o resultado da query para uma resposta em linguagem natural.

### ETL Analyst (`agents/etl_analyst.py`)
Agente com ferramentas (tool-calling) que oferece:
- `extract_load_tool` — extrai dados de uma API (URL) e salva em CSV/JSON/Parquet.
- `transform_load_tool` — gera e executa código Pandas (via LLM) para transformar um arquivo de dados conforme a pergunta do usuário e salva o resultado.

### Modelos (`Models/schema.py`)
Schemas Pydantic usados como estado dos grafos LangGraph (`AgentSchema`, `ETLAgentSchema`, `DataAgentSchema`, `RouterSchema`, `JudgeSchema`).

### Utilitários (`utils/`)
- `database.py` — conexão Postgres (psycopg2), extração de metadados de schema e execução de SQL.
- `etl_tools.py` — funções de extração de API e transformação com Pandas.
- `llm_pick.py` — seleciona o modelo de LLM (`low`, `medium`, `high`) via `ChatOpenAI`.

### Dados (`data/`)
Dataset de exemplo de um app de ride-sharing (`users.csv`, `vehicles.csv`, `rides.csv`, `payments.csv`, `ratings.csv`), com pastas `extract/` e `transform/` usadas como destino das operações de ETL.

### `feed_db.py`
Script utilitário que cria o schema no PostgreSQL (tabelas `users`, `vehicles`, `rides`, `payments`, `ratings` com FKs e índices) e carrega os CSVs de `data/` via `COPY`.

## Pré-requisitos

- Python >= 3.12
- PostgreSQL acessível
- [uv](https://docs.astral.sh/uv/) (o projeto usa `pyproject.toml` + `uv.lock`)

## Instalação

```bash
uv sync
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com:

```env
OPENAI_API_KEY=sua_chave_openai

host=localhost
port=5432
database=nome_do_banco
user=usuario_postgres
password=senha_postgres
```

## Uso

### 1. Popular o banco de dados (opcional, dataset de exemplo)

```bash
python feed_db.py
```

### 2. Executar o agente principal

```bash
python agents/data_agent.py
```

Também é possível executar cada subagente isoladamente:

```bash
python agents/sql_analyst.py
python agents/etl_analyst.py
```

Cada script, ao rodar como `__main__`, também exporta um diagrama Mermaid do grafo (`*_graph.png`) na raiz do projeto.

## Segurança

O SQL Analyst possui uma etapa dedicada (`is_safe_sql`) que atua como guarda-corpo, impedindo a execução de qualquer instrução SQL que altere dados ou estrutura do banco — apenas consultas de leitura são executadas.
