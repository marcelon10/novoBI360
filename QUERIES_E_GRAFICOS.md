# BI360 — Queries GraphQL e Visualizações

Este documento descreve todas as queries GraphQL utilizadas pelo sistema, as tabelas do banco de dados consultadas e os gráficos/componentes gerados a partir de cada resposta.

---

## Parâmetros comuns a todas as queries

| Parâmetro  | Tipo     | Descrição |
|------------|----------|-----------|
| `customer` | `String` | Identificador do cliente (ex: `"usiminas"`). Usado para montar o nome da view (`mview_process_<customer>`). |
| `source`   | `String` | Conexão de banco utilizada. `"internal"` (padrão) ou `"multi_tenancy"`. Passado via URL: `?source=multi_tenancy`. |
| `grain`    | `String` | Granularidade temporal: `"day"`, `"week"` ou `"month"`. |
| `filters`  | `[FilterInput]` | Lista de filtros dinâmicos com `field`, `value` e `operator` (`eq`, `gte`, `lte`, `in`). |

---

## Aba: Visão Geral

Consolida dados das três áreas operacionais em uma única tela de resumo. Dispara as mesmas queries das outras abas, mas exibe apenas os gráficos principais de cada uma.

### KPIs exibidos

| Indicador | Origem |
|---|---|
| Total Ingressado | soma de `totalCount` da query de Ingresso |
| Ingresso Automático (%) | `totalAuto / totalCount` |
| Com Divergência (%) | `totalComDivergencia / totalCount` |
| Em Aberto | soma de `totalEmAberto` |
| Aguardando Usuário (%) | `totalEmAbertoHumanas / totalEmAberto` |

### Gráficos

| Título | Tipo | Dados |
|---|---|---|
| Notas por Tipo de Ingresso | Barras agrupadas + linha | Series de Ingresso |
| Divergências ao Longo do Tempo | Barras agrupadas + linha | Series de Divergência |
| Notas em Aberto por Pendência | Barras empilhadas | Series de Notas em Aberto |
| Top Fornecedores por Volume | Tabela estilo gráfico | `suppliers` de Ingresso |
| Principais Divergências | Tabela estilo gráfico | `types` de Divergência |
| Usuários com Notas em Aberto | Tabela estilo gráfico | `usuarios` de Notas em Aberto |

---

## Aba: Ingresso

### Query: `GetCaptura` (batch)

Enviada como uma única requisição GraphQL com três subconsultas.

```graphql
query GetCaptura($filters: [FilterInput!], $customer: String!, $grain: String!, $source: String!) {
    series: getCaptura(filters: $filters, customer: $customer, grain: $grain, source: $source) {
        date totalCount totalAuto documentType
    }
    suppliers: getCapturaFornecedores(filters: $filters, customer: $customer, source: $source) {
        supplierCnpj totalCount totalAuto documentType
    }
    cities: getCapturaCidades(filters: $filters, customer: $customer, source: $source) {
        currency totalCount totalAuto documentType
    }
}
```

#### `getCaptura` — série temporal

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    date_trunc('<grain>', process_created_at)::text,
    sum(total_notas) as total_count,
    sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
    document_type
FROM mview_process_<customer>
WHERE 1=1 <filtros>
GROUP BY 1, document_type
ORDER BY 1
```

**Campos retornados:** `date`, `totalCount`, `totalAuto`, `documentType`

#### `getCapturaFornecedores` — top fornecedores

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    coalesce(supplier_cnpj, 'N/A'),
    sum(total_notas) as total_count,
    sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
    document_type
FROM mview_process_<customer>
WHERE 1=1 <filtros>
GROUP BY supplier_cnpj, document_type
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `supplierCnpj`, `totalCount`, `totalAuto`, `documentType`

#### `getCapturaCidades` — top tomadores (AQUI ESTOU USANDO CUSTOMER_CNPJ, MAS SERIA NA VERDADE O NOME DA PREFEITURA DE ONDE A NOTA FOI EMITIDA, ALTERAR POSTERIORMENTE)

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    coalesce(customer_cnpj, 'Sem Cidade'),
    sum(total_notas) as total_count,
    sum(case when provider in ('CAPTURE', 'MAILBOX_CAPTURE') then total_notas else 0 end) as total_auto,
    document_type
FROM mview_process_<customer>
WHERE 1=1 <filtros>
GROUP BY currency, document_type
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `currency` (CNPJ tomador), `totalCount`, `totalAuto`, `documentType`

### KPIs — Ingresso

| Indicador | Cálculo |
|---|---|
| Total de Notas | `Σ totalCount` |
| Ingresso Automático (%) | `Σ totalAuto / Σ totalCount` |
| Notas Automáticas | `Σ totalAuto` |
| Ingresso Manual | `Σ totalCount − Σ totalAuto` |

### Gráficos — Ingresso

| Título | Tipo | Séries |
|---|---|---|
| Notas por Tipo de Ingresso | Barras agrupadas + linha secundária | Barras: Automático / Manual · Linha: % automático |
| Composição por Tipo de Documento | Barras empilhadas | Uma barra por `documentType` ao longo do tempo |
| Distribuição Percentual | Pizza | Participação de cada `documentType` no total |
| Top 10 Fornecedores | Tabela estilo gráfico | `supplierCnpj`, volume total e automático |
| Top 10 Tomadores / Cidades | Tabela estilo gráfico | `currency` (CNPJ tomador), volume total e automático |

### Query: `GetCapturaAnalitico` (paginada)

Acionada pela tabela analítica na parte inferior da aba.

```graphql
query GetCapturaAnalitico($limit: Int!, $offset: Int!, $customer: String!, $source: String!, $filters: [FilterInput!]) {
    getCapturaAnalitico(limit: $limit, offset: $offset, customer: $customer, source: $source, filters: $filters) {
        id supplierCnpj issueDate provider totalValue documentType
    }
}
```

**Tabela consultada (internal):** `tax_documents` filtrado por `c_id = '<customer>_prod'`

**Tabela consultada (multi_tenancy):** `vinvoice_tax_documents`

**Colunas exibidas na tabela:** ID Nota, CNPJ Fornecedor, Emissão, Ingresso (provider), Valor Total, Tipo

---

## Aba: Divergências

### Query: `GetDivergencia` (batch)

```graphql
query GetDivergencia($filters: [FilterInput!], $customer: String!, $grain: String!, $source: String!) {
    series: getDivergencia(filters: $filters, customer: $customer, grain: $grain, source: $source) {
        date totalCount totalComDivergencia documentType
    }
    suppliers: getDivergenciaFornecedores(filters: $filters, customer: $customer, source: $source) {
        supplierCnpj totalCount
    }
    types: getDivergenciaTipo(filters: $filters, customer: $customer, source: $source) {
        nomeDivergencia totalCount
    }
}
```

#### `getDivergencia` — série temporal

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    date_trunc('<grain>', process_created_at)::text,
    sum(total_notas) as total_count,
    sum(case when divergence_flag = 'Com Divergência' then total_notas else 0 end) as total_com_divergencia,
    document_type
FROM mview_process_<customer>
WHERE 1=1 <filtros>
GROUP BY 1, 4
ORDER BY 1
```

**Campos retornados:** `date`, `totalCount`, `totalComDivergencia`, `documentType`

#### `getDivergenciaFornecedores` — top fornecedores divergentes

**Tabela consultada:** `mview_divergence_<customer>`

```sql
SELECT
    supplier_cnpj,
    sum(total_divergencia) as total_count
FROM mview_divergence_<customer>
WHERE 1=1 <filtros>
GROUP BY supplier_cnpj
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `supplierCnpj`, `totalCount`

#### `getDivergenciaTipo` — tipos de divergência

**Tabela consultada:** `mview_divergence_<customer>`

```sql
SELECT
    nome_divergencia,
    sum(total_divergencia) as total_count
FROM mview_divergence_<customer>
WHERE 1=1 <filtros>
GROUP BY nome_divergencia
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `nomeDivergencia`, `totalCount`

### KPIs — Divergências

| Indicador | Cálculo |
|---|---|
| Total de Notas | `Σ totalCount` |
| Taxa de Divergência (%) | `Σ totalComDivergencia / Σ totalCount` |
| Notas Divergentes | `Σ totalComDivergencia` |
| Notas Saudáveis | `Σ totalCount − Σ totalComDivergencia` |

### Gráficos — Divergências

| Título | Tipo | Séries |
|---|---|---|
| Volume vs % Divergência | Barras agrupadas + linha secundária | Barras: Com Divergência / Sem Divergência · Linha: % divergente |
| Eficiência por Tipo de Documento | Barras 100% empilhadas | Com Divergência (%) vs Sem Divergência (%) por `documentType` |
| Composição das Divergências | Pizza | Participação de cada `documentType` nas divergências |
| Top 10 Fornecedores por Divergência | Tabela estilo gráfico | `supplierCnpj` e total de divergências |
| Top 10 Tipos de Divergência | Tabela estilo gráfico | `nomeDivergencia` e total |
| Evolução Temporal | Linhas com delta | Total Processado vs Com Divergência ao longo do tempo |

### Query: `GetDivergenciaAnalitico` (paginada)

```graphql
query GetDivergenciaAnalitico($limit: Int!, $offset: Int!, $customer: String!, $source: String!, $filters: [FilterInput!]) {
    getDivergenciaAnalitico(limit: $limit, offset: $offset, customer: $customer, source: $source, filters: $filters) {
        id nomeDivergencia idNota targetValue fieldValue createdAt
    }
}
```

**Tabela consultada (internal):** `divergences` filtrado por `c_id = '<customer>_prod'`

**Tabela consultada (multi_tenancy):** `vpmng_validation_records` com JOIN em `vpmng_validation_errors`

**Colunas exibidas na tabela:** ID, Divergência, ID Nota, Valor Esperado, Valor Real, Data

---

## Aba: Notas em Aberto

### Query: `GetNotasAberto` (batch)

```graphql
query GetNotasAberto($filters: [FilterInput!], $customer: String!, $grain: String!, $source: String!) {
    series: getNotasAberto(filters: $filters, customer: $customer, grain: $grain, source: $source) {
        date totalEmAberto totalEmAbertoHumanas
    }
    usuarios: getNotasAbertoUsuario(filters: $filters, customer: $customer, source: $source) {
        userName totalCount
    }
    tarefas: getNotasAbertoTarefa(filters: $filters, customer: $customer, source: $source) {
        nomeTarefa totalCount
    }
}
```

#### `getNotasAberto` — série temporal

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    date_trunc('<grain>', process_created_at)::text,
    sum(case when horas_em_aberto is not null then total_notas else 0 end) as total_em_aberto,
    sum(case when horas_em_aberto is not null and user_name is not null then total_notas else 0 end) as total_em_aberto_humanas
FROM mview_process_<customer>
WHERE horas_em_aberto is not null and user_name is not null <filtros>
GROUP BY 1
ORDER BY 1
```

**Campos retornados:** `date`, `totalEmAberto`, `totalEmAbertoHumanas`

#### `getNotasAbertoUsuario` — top usuários

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    user_name,
    sum(total_notas) as total_count
FROM mview_process_<customer>
WHERE user_name is not null and horas_em_aberto is not null <filtros>
GROUP BY user_name
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `userName`, `totalCount`

#### `getNotasAbertoTarefa` — top tarefas

**Tabela consultada:** `mview_process_<customer>`

```sql
SELECT
    last_task_name,
    sum(total_notas) as total_count
FROM mview_process_<customer>
WHERE user_name is not null and horas_em_aberto is not null <filtros>
GROUP BY last_task_name
ORDER BY total_count DESC
LIMIT 10
```

**Campos retornados:** `nomeTarefa`, `totalCount`

### KPIs — Notas em Aberto

| Indicador | Cálculo |
|---|---|
| Total em Aberto | `Σ totalEmAberto` |
| Interação Humana (%) | `Σ totalEmAbertoHumanas / Σ totalEmAberto` |
| Pendência Humana | `Σ totalEmAbertoHumanas` |
| Pendência Sistema | `Σ totalEmAberto − Σ totalEmAbertoHumanas` |

### Gráficos — Notas em Aberto

| Título | Tipo | Séries |
|---|---|---|
| Volume em Aberto por Tipo de Pendência | Barras empilhadas + linha secundária | Barras: Pendência Humana / Pendência Sistema · Linha: % humano |
| Evolução Temporal | Linhas com delta | Total Em Aberto vs Pendente Humano |
| Composição de Pendências | Pizza | Humana vs Sistema |
| Top 10 Tarefas em Aberto | Tabela estilo gráfico | `nomeTarefa` e total |
| Top 10 Usuários com Notas | Tabela estilo gráfico | `userName` e total |

### Query: `GetNotasAbertoAnalitico` (paginada)

```graphql
query GetNotasAbertoAnalitico($limit: Int!, $offset: Int!, $customer: String!, $source: String!, $filters: [FilterInput!]) {
    getNotasAbertoAnalitico(limit: $limit, offset: $offset, customer: $customer, source: $source, filters: $filters) {
        id nomeTarefa userName createdAt
    }
}
```

**Tabela consultada (internal):** `tax_documents` onde `completed_at is null AND assigned_user is not null`

**Tabela consultada (multi_tenancy):** `vpmng_process_instances` com JOINs em `vpmng_tasks`, `vpmng_task_definitions`, `vportal_users`, `vportal_user_groups`, `vcpr_commercial_partners`

**Colunas exibidas na tabela:** ID, Tarefa, Usuário, Data

---

## Query auxiliar: Opções de Filtro

Carregada ao trocar de aba ou ao mudar o `customer` na URL. Popula os dropdowns do painel lateral de filtros.

```graphql
query GetOptions($customer: String!, $source: String!) {
    getFilterOptions(customer: $customer, source: $source)
}
```

**Tabela consultada:** `mview_process_<customer>`

```sql
-- fluxos
SELECT DISTINCT process_name  FROM mview_process_<customer> WHERE process_name  IS NOT NULL ORDER BY 1

-- fornecedores
SELECT DISTINCT supplier_cnpj FROM mview_process_<customer> WHERE supplier_cnpj IS NOT NULL ORDER BY 1

-- tomadores
SELECT DISTINCT customer_cnpj FROM mview_process_<customer> WHERE customer_cnpj IS NOT NULL ORDER BY 1
```

**Dropdowns populados:** Fluxo, CNPJ Fornecedor, CNPJ Tomador. O dropdown de Tipo de Documento é fixo: `Vinvoice::MaterialInvoice` e `Vinvoice::ServiceInvoice`.
