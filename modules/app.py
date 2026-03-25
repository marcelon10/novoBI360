import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from flask_caching import Cache
import logging
import sys
import urllib.parse
from datetime import datetime

# Importações de módulos locais
import layouts
import api_client
from constants import HTML_HOMEPAGE_CONTENT

# --- CONFIGURAÇÃO DE LOGGING ---
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

# --- INICIALIZAÇÃO DO APP ---
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
)
server = app.server

# --- CONFIGURAÇÃO DE CACHE ---
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache', 
    'CACHE_DEFAULT_TIMEOUT': 300 
})

# --- FUNÇÕES MEMOIZADAS (CACHE) ---
@cache.memoize()
def get_cached_captura_data(grain, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_full_captura_data(grain=grain, customer=customer, filters=filters_list)

@cache.memoize()
def get_cached_divergencia_data(grain, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_full_divergencia_data(grain=grain, customer=customer, filters=filters_list)

@cache.memoize()
def get_cached_notas_aberto_data(grain, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_full_notas_aberto_data(grain=grain, customer=customer, filters=filters_list)

@cache.memoize()
def get_cached_filter_options(customer):
    return api_client.get_filter_options(customer)

@cache.memoize()
def get_cached_captura_analitico(limit, offset, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_captura_analitico(limit=limit, offset=offset, customer=customer, filters=filters_list)

@cache.memoize()
def get_cached_divergencia_analitico(limit, offset, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_divergencia_analitico(limit=limit, offset=offset, customer=customer, filters=filters_list)

@cache.memoize()
def get_cached_notas_aberto_analitico(limit, offset, customer, filters_tuple):
    filters_list = [dict(f) for f in filters_tuple]
    return api_client.get_notas_aberto_analitico(limit=limit, offset=offset, customer=customer, filters=filters_list)


# --- STRATEGY: GET CUSTOMER FROM SEARCH ---
def get_customer_from_search(search):
    if search:
        parsed = urllib.parse.parse_qs(search.lstrip('?'))
        if 'customer' in parsed:
            return parsed['customer'][0]
    return 'usiminas'


# --- LÓGICA MODULAR PARA TABELAS ANALÍTICAS ---
def fetch_table_data(page_current, page_size, n_clicks, tab, start, end, doc_types, status, fluxo, tomador, fornecedor, search):
    """
    Função centralizada para processar dados das tabelas de ambas as abas.
    """
    p_current = page_current if page_current is not None else 0
    p_size = page_size if page_size is not None else 10
    offset = p_current * p_size
    
    api_filters = []
    
    # Filtros de Data
    if start: api_filters.append({'field': 'process_created_at', 'value': start, 'operator': 'gte'})
    if end:   api_filters.append({'field': 'process_created_at', 'value': end, 'operator': 'lte'})
    
    # Helper para formatar filtros de multi-seleção (IN)
    def add_in_filter(field, values):
        if values and isinstance(values, list):
            formatted = ", ".join([f"'{v}'" for v in values])
            api_filters.append({'field': field, 'value': formatted, 'operator': 'in'})

    add_in_filter('document_type', doc_types)
    add_in_filter('process_name', fluxo)
    add_in_filter('supplier_cnpj', fornecedor)
    add_in_filter('customer_cnpj', tomador)
    
    if status: 
        api_filters.append({'field': 'provider', 'value': status, 'operator': 'eq'})

    customer_id = get_customer_from_search(search)
    filters_tuple = tuple(tuple(d.items()) for d in api_filters)

    if tab == 'tab-divergencia':
        cols = [
            {"name": "ID", "id": "id"},
            {"name": "Divergência", "id": "nomeDivergencia"},
            {"name": "ID Nota", "id": "idNota"},
            {"name": "Valor Esperado", "id": "targetValue"},
            {"name": "Valor Real", "id": "fieldValue"},
            {"name": "Data", "id": "createdAt"}
        ]
        data = get_cached_divergencia_analitico(limit=p_size, offset=offset, customer=customer_id, filters_tuple=filters_tuple)
    elif tab == 'tab-notas-aberto':
        cols = [
            {"name": "ID", "id": "id"},
            {"name": "Tarefa", "id": "nomeTarefa"},
            {"name": "Usuário", "id": "userName"},
            {"name": "Data", "id": "createdAt"}
        ]
        data = get_cached_notas_aberto_analitico(limit=p_size, offset=offset, customer=customer_id, filters_tuple=filters_tuple)
    else:
        cols = [
            {"name": "ID Nota", "id": "id"},
            {"name": "CNPJ Fornecedor", "id": "supplierCnpj"},
            {"name": "Emissão", "id": "issueDate"},
            {"name": "Ingresso", "id": "provider"},
            {"name": "Valor Total", "id": "totalValue"},
            {"name": "Tipo", "id": "documentType"}
        ]
        data = get_cached_captura_analitico(limit=p_size, offset=offset, customer=customer_id, filters_tuple=filters_tuple)
        
    return data, cols

# --- LAYOUT PRINCIPAL ---
tab_style = {'backgroundColor': '#1f2937', 'color': '#d1d5db'}
selected_style = {'backgroundColor': '#8B5CF6', 'color': 'white'}

app.layout = html.Div(style={'backgroundColor': '#111827', 'minHeight': '100vh', 'padding': '20px'}, children=[
    dcc.Location(id='url'),
    
    # Botão Flutuante de Filtros
    html.Button(
        html.I(className="fas fa-filter"),
        id="open-filters",
        n_clicks=0,
        style={
            'position': 'fixed', 'top': '20px', 'right': '20px', 'zIndex': '1000',
            'backgroundColor': '#8B5CF6', 'color': 'white', 'border': 'none',
            'borderRadius': '50%', 'width': '50px', 'height': '50px', 'boxShadow': '0 4px 10px rgba(0,0,0,0.3)'
        }
    ),

    # Sidebar de Filtros (Offcanvas)
    dbc.Offcanvas(
        id="sidebar-filters",
        title="Filtros da Operação",
        is_open=False,
        placement="end",
        style={'backgroundColor': '#1f2937', 'color': 'white'},
        children=[
            html.Div([
                html.P("Período", className="mb-1"),
                dcc.DatePickerRange(
                    id='filter-date',
                    start_date='2025-01-01',
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    style={'width': '100%'}
                ),
                
                html.P("Tipo de Documento", className="mt-4 mb-1"),
                dcc.Dropdown(id='filter-doc', multi=True, placeholder="Selecione...", className="bg-dark text-white border-secondary"),
                
                html.P("Status", className="mt-4 mb-1"),
                dcc.Dropdown(
                    id='filter-status',
                    options=['CAPTURE', 'MAILBOX_CAPTURE', 'INTERNAL_USER', 'EXTERNAL_USER'],
                    placeholder="Selecione...",
                    className="dark-dropdown"
                ),
                
                html.P("Fluxo", className="mt-4 mb-1"),
                dcc.Dropdown(id='filter-fluxo', multi=True, placeholder="Selecione...", className="dark-dropdown"),

                html.P("CNPJ Tomador", className="mt-4 mb-1"),
                dcc.Dropdown(id='filter-tomador', multi=True, placeholder="Selecione...", className="dark-dropdown"),

                html.P("CNPJ Fornecedor", className="mt-4 mb-1"),
                dcc.Dropdown(id='filter-fornecedor', multi=True, placeholder="Selecione...", className="dark-dropdown"),
                
                html.P("Granularidade", className="mt-4 mb-1"),
                dcc.Dropdown(
                    id='filter-grain',
                    options=[
                        {'label': 'Diário', 'value': 'day'},
                        {'label': 'Semanal', 'value': 'week'},
                        {'label': 'Mensal', 'value': 'month'}
                    ],
                    value='month',
                    clearable=False,
                    className="dark-dropdown"
                ),
                
                dbc.Button(
                    "Aplicar Filtros", 
                    id="btn-apply", 
                    n_clicks=0, 
                    className="w-100 mt-5",
                    style={'backgroundColor': '#8B5CF6', 'border': 'none'}
                )
            ])
        ],
    ),

    # Navegação por Abas
    dcc.Tabs(id="tabs", value='tab-resumo', children=[
        dcc.Tab(label='Resumo', value='tab-resumo', style=tab_style, selected_style=selected_style),
        dcc.Tab(label='Captura', value='tab-captura', style=tab_style, selected_style=selected_style),
        dcc.Tab(label='Divergência', value='tab-divergencia', style=tab_style, selected_style=selected_style),
        dcc.Tab(label='Notas em Aberto', value='tab-notas-aberto', style=tab_style, selected_style=selected_style),
    ]),
    
    html.Div(id='tabs-content', style={'marginTop': '20px'})
])

# --- CALLBACKS ---

@app.callback(
    Output("sidebar-filters", "is_open"),
    Input("open-filters", "n_clicks"),
    State("sidebar-filters", "is_open"),
)
def toggle_offcanvas(n1, is_open):
    if n1: return not is_open
    return is_open

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('btn-apply', 'n_clicks'),
    Input('url', 'search'),
    State('filter-date', 'start_date'),
    State('filter-date', 'end_date'),
    State('filter-doc', 'value'),
    State('filter-status', 'value'),
    State('filter-fluxo', 'value'),
    State('filter-tomador', 'value'),
    State('filter-fornecedor', 'value'),
    State('filter-grain', 'value')
)
def render_content(tab, n_clicks, search, start, end, doc_types, status, fluxo, tomador, fornecedor, grain):
    customer_id = get_customer_from_search(search)
    
    # Construção dos filtros para API
    api_filters = []
    if start: api_filters.append({'field': 'process_created_at', 'value': start, 'operator': 'gte'})
    if end:   api_filters.append({'field': 'process_created_at', 'value': end, 'operator': 'lte'})
    
    def add_in_filter(field, values):
        if values:
            formatted = ", ".join([f"'{v}'" for v in values])
            api_filters.append({'field': field, 'value': formatted, 'operator': 'in'})

    add_in_filter('document_type', doc_types)
    add_in_filter('process_name', fluxo)
    add_in_filter('supplier_cnpj', fornecedor)
    add_in_filter('customer_cnpj', tomador)
    
    if status: api_filters.append({'field': 'provider', 'value': status, 'operator': 'eq'})
    
    filters_tuple = tuple(tuple(d.items()) for d in api_filters)

    if tab == 'tab-resumo':
        return layouts.get_resumo_iframe(HTML_HOMEPAGE_CONTENT)
    
    if tab == 'tab-captura':
        dashboard_data = get_cached_captura_data(grain, customer_id, filters_tuple)
        return layouts.get_captura_layout(
            selected_grain={'day':'D','week':'W','month':'ME'}.get(grain, 'ME'), 
            api_data=dashboard_data, 
            api_grain=grain
        )
        
    if tab == 'tab-divergencia':
        divergencia_data = get_cached_divergencia_data(grain, customer_id, filters_tuple)
        return layouts.get_divergencia_layout(
            selected_grain={'day':'D','week':'W','month':'ME'}.get(grain, 'ME'), 
            api_data=divergencia_data, 
            api_grain=grain
        )
        
    if tab == 'tab-notas-aberto':
        notas_aberto_data = get_cached_notas_aberto_data(grain, customer_id, filters_tuple)
        return layouts.get_notas_aberto_layout(
            selected_grain={'day':'D','week':'W','month':'ME'}.get(grain, 'ME'), 
            api_data=notas_aberto_data, 
            api_grain=grain
        )
        
    return html.Div("Conteúdo não encontrado", style={'color': 'white'})

# Callbacks Independentes para as Tabelas
@app.callback(
    [Output('tabela-analitica-captura', 'data'), Output('tabela-analitica-captura', 'columns')],
    [Input('tabela-analitica-captura', "page_current"), Input('tabela-analitica-captura', "page_size"), Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'), State('filter-date', 'end_date'), 
     State('filter-doc', 'value'), State('filter-status', 'value'), State('filter-fluxo', 'value'), 
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'), State('url', 'search')]
)
def update_captura_table(*args):
    return fetch_table_data(*args)

@app.callback(
    [Output('tabela-analitica-divergencias', 'data'), Output('tabela-analitica-divergencias', 'columns')],
    [Input('tabela-analitica-divergencias', "page_current"), Input('tabela-analitica-divergencias', "page_size"), Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'), State('filter-date', 'end_date'), 
     State('filter-doc', 'value'), State('filter-status', 'value'), State('filter-fluxo', 'value'), 
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'), State('url', 'search')]
)
def update_divergencia_table(*args):
    return fetch_table_data(*args)

@app.callback(
    [Output('tabela-analitica-notas-aberto', 'data'), Output('tabela-analitica-notas-aberto', 'columns')],
    [Input('tabela-analitica-notas-aberto', "page_current"), Input('tabela-analitica-notas-aberto', "page_size"), Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'), State('filter-date', 'end_date'), 
     State('filter-doc', 'value'), State('filter-status', 'value'), State('filter-fluxo', 'value'), 
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'), State('url', 'search')]
)
def update_notas_aberto_table(*args):
    return fetch_table_data(*args)

@app.callback(
    Output('filter-fluxo', 'options'),
    Output('filter-fornecedor', 'options'),
    Output('filter-tomador', 'options'),
    Output('filter-doc', 'options'),
    Input('tabs', 'value'),
    Input('url', 'search')
)
def load_dropdown_options(tab, search):
    customer_id = get_customer_from_search(search)
    options = get_cached_filter_options(customer_id)
    return (
        options.get('fluxos', []), 
        options.get('fornecedores', []), 
        options.get('tomadores', []),
        ['Vinvoice::MaterialInvoice', 'Vinvoice::ServiceInvoice'] # Exemplo estático ou vindo da API
    )

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)