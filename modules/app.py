import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import layouts
from constants import HTML_HOMEPAGE_CONTENT
from datetime import datetime
from dash import Input, Output, callback
import logging
import sys
import api_client
from flask_caching import Cache

# Configure logging to output to the terminal (stdout)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Specifically target the Flask and Dash loggers
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME] # Added FontAwesome
)

# Configuração do Cache (em memória para ser ultra-rápido)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache', 
    'CACHE_DEFAULT_TIMEOUT': 300 # 5 minutos de "frescor" nos dados
})

@cache.memoize()
def get_cached_dashboard_data(grain, customer, filters_tuple):
    # O GraphQL deu erro porque recebeu uma tupla/lista de listas. 
    # Precisamos converter cada tupla interna de volta para um dict.
    filters_list = [dict(f) for f in filters_tuple]
    
    return api_client.get_full_dashboard_data(
        grain=grain, 
        customer=customer, 
        filters=filters_list # Agora enviamos a lista de dicionários correta
    )
    
@cache.memoize(timeout=3600) # Cache de 1 hora
def get_cached_options(customer):
    return api_client.get_filter_options(customer)

tab_style = {'backgroundColor': '#1f2937', 'color': '#d1d5db'}
selected_style = {'backgroundColor': '#8B5CF6', 'color': 'white'}

app.layout = html.Div(style={'backgroundColor': '#111827', 'minHeight': '100vh', 'padding': '20px'}, children=[
    dcc.Location(id='url'),
    
    # DISCRETE FLOATING BUTTON (Right Side)
    html.Button(
        html.I(className="fas fa-filter"), # Filter Icon
        id="open-filters",
        n_clicks=0,
        style={
            'position': 'fixed', 'top': '20px', 'right': '20px', 'zIndex': '1000',
            'backgroundColor': '#8B5CF6', 'color': 'white', 'border': 'none',
            'borderRadius': '50%', 'width': '50px', 'height': '50px', 'boxShadow': '0 4px 10px rgba(0,0,0,0.3)'
        }
    ),

    # SIDEBAR (Offcanvas)
    dbc.Offcanvas(
        id="sidebar-filters",
        title="Filtros da Operação",
        is_open=False,
        placement="end", # Opens from the right
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
                dcc.Dropdown(
                    id='filter-doc',
                    options=['Vinvoice::MaterialInvoice'],
                    multi=True,
                    placeholder="Selecione...",
                    className="dark-dropdown"
                ),
                
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

                #html.P("Moeda", className="mt-4 mb-1"),
                #dcc.Dropdown(id='filter-moeda', placeholder="Selecione...", className="dark-dropdown"),
                
                html.P("Granularidade", className="mt-4 mb-1"),
                dcc.Dropdown(
                    id='filter-grain',
                    options=[
                        {'label': 'Diário', 'value': 'day'},
                        {'label': 'Semanal', 'value': 'week'},
                        {'label': 'Mensal', 'value': 'month'}
                    ],
                    value='month', # Padrão
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

    # MAIN CONTENT
    dcc.Tabs(id="tabs", value='tab-resumo', children=[
        dcc.Tab(label='Resumo', value='tab-resumo', style=tab_style, selected_style=selected_style),
        dcc.Tab(label='Captura', value='tab-captura', style=tab_style, selected_style=selected_style),
    ]),
    html.Div(id='tabs-content', style={'marginTop': '20px'})
])

# CALLBACK TO OPEN/CLOSE SIDEBAR
@app.callback(
    Output("sidebar-filters", "is_open"),
    Input("open-filters", "n_clicks"),
    [State("sidebar-filters", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# MAIN RENDER CALLBACK
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('btn-apply', 'n_clicks'),
    State('filter-date', 'start_date'),
    State('filter-date', 'end_date'),
    State('filter-doc', 'value'),
    State('filter-status', 'value'),
    State('filter-fluxo', 'value'),
    State('filter-tomador', 'value'),
    State('filter-fornecedor', 'value'),
    State('filter-grain', 'value')
)
def render_content(tab, n_clicks, start, end, doc_types, status, fluxo, tomador, fornecedor, grain):
    # Mapeamento de grão para o Pandas
    grain_map = {'day': 'D', 'week': 'W', 'month': 'ME'}
    pd_grain = grain_map.get(grain, 'ME')
    
    # Construção dos filtros
    api_filters = []
    if start: api_filters.append({'field': 'process_created_at', 'value': start, 'operator': 'gte'})
    if end:   api_filters.append({'field': 'process_created_at', 'value': end, 'operator': 'lte'})
    if doc_types: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in doc_types])
        api_filters.append({'field': 'document_type', 'value': formatted_docs, 'operator': 'in'})
    if status: 
        api_filters.append({'field': 'provider', 'value': status, 'operator': 'eq'})
    if fluxo: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in fluxo])
        api_filters.append({'field': 'process_name', 'value': formatted_docs, 'operator': 'in'})
    if fornecedor: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in fornecedor])
        api_filters.append({'field': 'supplier_cnpj', 'value': formatted_docs, 'operator': 'in'})
    if tomador: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in tomador])
        api_filters.append({'field': 'customer_cnpj', 'value': formatted_docs, 'operator': 'in'})

    if tab == 'tab-resumo':
        return layouts.get_resumo_iframe(HTML_HOMEPAGE_CONTENT)
    
    if tab == 'tab-captura':
        # 1. Transformamos a lista de dicts em tupla de tuplas para o cache aceitar como chave
        filters_tuple = tuple(tuple(d.items()) for d in api_filters)
        
        # 2. Chamamos a função memoizada
        dashboard_data = get_cached_dashboard_data(grain, 'aegea', filters_tuple)
        
        # 3. Renderizamos o layout
        grain_map = {'day': 'D', 'week': 'W', 'month': 'ME'}
        return layouts.get_captura_layout(
            selected_grain=grain_map.get(grain, 'ME'), 
            api_data=dashboard_data, 
            api_grain=grain
        )
        
    return html.Div("Conteúdo em desenvolvimento", style={'color': 'white'})

@callback(
    Output('tabela-analitica', 'data'),
    Input('tabela-analitica', "page_current"),
    Input('tabela-analitica', "page_size"),
    Input('btn-apply', 'n_clicks'),
    State('filter-date', 'start_date'),
    State('filter-date', 'end_date'),
    State('filter-doc', 'value'),    # Corrigido de filter-doc-type para filter-doc
    State('filter-status', 'value'),
    State('filter-fluxo', 'value'),
    State('filter-tomador', 'value'),
    State('filter-fornecedor', 'value'),# Este já estava correto na lista
)
def update_table(page_current, page_size, n_clicks, start, end, doc_types, status, fluxo, tomador, fornecedor):
    # O restante da lógica permanece...
    current_page = page_current if page_current is not None else 0
    offset = current_page * page_size
    
    api_filters = []
    
    # Datas
    if start: api_filters.append({'field': 'process_created_at', 'value': start, 'operator': 'gte'})
    if end:   api_filters.append({'field': 'process_created_at', 'value': end, 'operator': 'lte'})
    
    # Document Types (usando o id filter-doc)
    if doc_types:
        formatted_docs = ", ".join([f"'{item}'" for item in doc_types])
        api_filters.append({'field': 'type', 'value': formatted_docs, 'operator': 'in'})
    
    # Status
    if status:
        api_filters.append({'field': 'provider', 'value': status, 'operator': 'eq'})
        
    if fluxo: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in fluxo])
        api_filters.append({'field': 'process_name', 'value': formatted_docs, 'operator': 'in'})
    if fornecedor: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in fornecedor])
        api_filters.append({'field': 'supplier_cnpj', 'value': formatted_docs, 'operator': 'in'})
    if tomador: 
        # Formatando para o operador 'in' do SQL
        formatted_docs = ", ".join([f"'{item}'" for item in tomador])
        api_filters.append({'field': 'customer_cnpj', 'value': formatted_docs, 'operator': 'in'})

    
    return api_client.get_analitico(
        limit=page_size, 
        offset=offset, 
        customer='aegea', 
        filters=api_filters
    )

@app.callback(
    Output('filter-fluxo', 'options'),
    Output('filter-fornecedor', 'options'),
    Output('filter-tomador', 'options'),
    Input('tabs', 'value') # Ou outro gatilho de inicialização
)
def load_dropdown_options(tab):
    options = api_client.get_filter_options('aegea')
    
    fluxo_opts = options.get('fluxos', [])
    forn_opts = options.get('fornecedores', [])
    tom_opts = options.get('tomadores', [])
    
    return fluxo_opts, forn_opts, tom_opts

if __name__ == '__main__':
    app.run(
        debug=True, 
        host="0.0.0.0", 
        port=8050,
        dev_tools_ui=True,           # Shows error popups in browser
        dev_tools_props_check=True,  # Logs if you pass wrong data types to components
        dev_tools_silence_routes_logging=False,
        dev_tools_hot_reload=False
    )