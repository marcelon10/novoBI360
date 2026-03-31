import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask_caching import Cache
import logging
import sys
import urllib.parse
from datetime import datetime

import layouts
import api_client
from constants import HTML_HOMEPAGE_CONTENT

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# ── Brand tokens ──────────────────────────────────────────────────────────────
C_PURPLE       = '#592a9e'
C_PURPLE_LIGHT = '#783dbc'
C_ORANGE       = '#e16500'
C_NAVY         = '#151731'
C_GRAY         = '#6b7280'
C_GRAY_LIGHT   = '#e5e7eb'
C_WHITE        = '#ffffff'
C_BG           = '#f5f3ff'
FONT           = 'Ubuntu, sans-serif'

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        'https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap',
    ],
)
server = app.server

# ── Cache ─────────────────────────────────────────────────────────────────────
cache = Cache(app.server, config={
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DIR': '/tmp/bi360_cache',
    'CACHE_DEFAULT_TIMEOUT': 300,
})

# ── Memoized data fetchers ────────────────────────────────────────────────────
@cache.memoize()
def get_cached_captura_data(grain, customer, filters_tuple):
    return api_client.get_full_captura_data(grain=grain, customer=customer,
                                             filters=[dict(f) for f in filters_tuple])

@cache.memoize()
def get_cached_divergencia_data(grain, customer, filters_tuple):
    return api_client.get_full_divergencia_data(grain=grain, customer=customer,
                                                 filters=[dict(f) for f in filters_tuple])

@cache.memoize()
def get_cached_notas_aberto_data(grain, customer, filters_tuple):
    return api_client.get_full_notas_aberto_data(grain=grain, customer=customer,
                                                  filters=[dict(f) for f in filters_tuple])

@cache.memoize()
def get_cached_filter_options(customer):
    return api_client.get_filter_options(customer)

@cache.memoize()
def get_cached_captura_analitico(limit, offset, customer, filters_tuple):
    return api_client.get_captura_analitico(limit=limit, offset=offset, customer=customer,
                                             filters=[dict(f) for f in filters_tuple])

@cache.memoize()
def get_cached_divergencia_analitico(limit, offset, customer, filters_tuple):
    return api_client.get_divergencia_analitico(limit=limit, offset=offset, customer=customer,
                                                 filters=[dict(f) for f in filters_tuple])

@cache.memoize()
def get_cached_notas_aberto_analitico(limit, offset, customer, filters_tuple):
    return api_client.get_notas_aberto_analitico(limit=limit, offset=offset, customer=customer,
                                                  filters=[dict(f) for f in filters_tuple])

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_customer_from_search(search):
    if search:
        parsed = urllib.parse.parse_qs(search.lstrip('?'))
        if 'customer' in parsed:
            return parsed['customer'][0]
    return 'usiminas'


def build_filters(start, end, doc_types, status, fluxo, tomador, fornecedor):
    filters = []
    if start: filters.append({'field': 'process_created_at', 'value': start,  'operator': 'gte'})
    if end:   filters.append({'field': 'process_created_at', 'value': end,    'operator': 'lte'})

    def add_in(field, values):
        if values and isinstance(values, list):
            filters.append({'field': field,
                             'value': ', '.join(f"'{v}'" for v in values),
                             'operator': 'in'})

    add_in('document_type', doc_types)
    add_in('process_name',  fluxo)
    add_in('supplier_cnpj', fornecedor)
    add_in('customer_cnpj', tomador)
    if status:
        filters.append({'field': 'provider', 'value': status, 'operator': 'eq'})
    return filters


def fetch_table_data(page_current, page_size, n_clicks, tab,
                     start, end, doc_types, status, fluxo, tomador, fornecedor, search):
    p   = page_current or 0
    ps  = page_size or 10
    off = p * ps
    filters        = build_filters(start, end, doc_types, status, fluxo, tomador, fornecedor)
    customer_id    = get_customer_from_search(search)
    filters_tuple  = tuple(tuple(d.items()) for d in filters)

    if tab == 'tab-divergencia':
        cols = [
            {'name': 'ID',           'id': 'id'},
            {'name': 'Divergência',  'id': 'nomeDivergencia'},
            {'name': 'ID Nota',      'id': 'idNota'},
            {'name': 'Valor Esperado','id': 'targetValue'},
            {'name': 'Valor Real',   'id': 'fieldValue'},
            {'name': 'Data',         'id': 'createdAt'},
        ]
        data = get_cached_divergencia_analitico(ps, off, customer_id, filters_tuple)
    elif tab == 'tab-notas-aberto':
        cols = [
            {'name': 'ID',      'id': 'id'},
            {'name': 'Tarefa',  'id': 'nomeTarefa'},
            {'name': 'Usuário', 'id': 'userName'},
            {'name': 'Data',    'id': 'createdAt'},
        ]
        data = get_cached_notas_aberto_analitico(ps, off, customer_id, filters_tuple)
    else:
        cols = [
            {'name': 'ID Nota',         'id': 'id'},
            {'name': 'CNPJ Fornecedor', 'id': 'supplierCnpj'},
            {'name': 'Emissão',         'id': 'issueDate'},
            {'name': 'Ingresso',        'id': 'provider'},
            {'name': 'Valor Total',     'id': 'totalValue'},
            {'name': 'Tipo',            'id': 'documentType'},
        ]
        data = get_cached_captura_analitico(ps, off, customer_id, filters_tuple)

    return data, cols


# ── Shared styles ─────────────────────────────────────────────────────────────
TAB_STYLE = {
    'padding': '8px 20px',
    'border': 'none',
    'borderBottom': f'2px solid transparent',
    'backgroundColor': 'transparent',
    'color': C_GRAY,
    'fontFamily': FONT,
    'fontWeight': '500',
    'fontSize': '14px',
    'cursor': 'pointer',
}
TAB_SELECTED = {
    **TAB_STYLE,
    'color': C_PURPLE,
    'borderBottom': f'2px solid {C_PURPLE}',
    'fontWeight': '700',
}

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        'backgroundColor': C_BG,
        'minHeight': '100vh',
        'fontFamily': FONT,
    },
    children=[
        dcc.Location(id='url'),

        # ── Header ────────────────────────────────────────────────────────────
        html.Div(
            style={
                'backgroundColor': C_WHITE,
                'borderBottom': f'1px solid {C_GRAY_LIGHT}',
                'padding': '0 32px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'height': '60px',
                'position': 'sticky',
                'top': '0',
                'zIndex': '100',
                'boxShadow': '0 1px 4px rgba(0,0,0,0.06)',
            },
            children=[
                # Logo / title
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                    children=[
                        html.Span('√', style={
                            'color': C_ORANGE, 'fontSize': '28px',
                            'fontWeight': '900', 'lineHeight': '1',
                        }),
                        html.Span('360', style={
                            'color': C_PURPLE, 'fontSize': '22px',
                            'fontWeight': '700', 'fontFamily': FONT,
                        }),
                        html.Span('BI', style={
                            'backgroundColor': C_PURPLE,
                            'color': C_WHITE,
                            'fontSize': '11px',
                            'fontWeight': '700',
                            'padding': '2px 8px',
                            'borderRadius': '12px',
                            'marginLeft': '4px',
                            'fontFamily': FONT,
                        }),
                    ],
                ),
                # Filter button
                html.Button(
                    [html.I(className='fas fa-sliders-h'), ' Filtros'],
                    id='open-filters',
                    n_clicks=0,
                    style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'gap': '8px',
                        'backgroundColor': C_PURPLE,
                        'color': C_WHITE,
                        'border': 'none',
                        'borderRadius': '8px',
                        'padding': '8px 18px',
                        'fontSize': '13px',
                        'fontWeight': '600',
                        'fontFamily': FONT,
                        'cursor': 'pointer',
                    },
                ),
            ],
        ),

        # ── Tab bar ───────────────────────────────────────────────────────────
        html.Div(
            style={
                'backgroundColor': C_WHITE,
                'borderBottom': f'1px solid {C_GRAY_LIGHT}',
                'padding': '0 32px',
            },
            children=[
                dcc.Tabs(
                    id='tabs',
                    value='tab-resumo',
                    style={'border': 'none'},
                    children=[
                        dcc.Tab(label='Visão Geral',    value='tab-resumo',
                                style=TAB_STYLE, selected_style=TAB_SELECTED),
                        dcc.Tab(label='Ingresso',       value='tab-captura',
                                style=TAB_STYLE, selected_style=TAB_SELECTED),
                        dcc.Tab(label='Divergências',   value='tab-divergencia',
                                style=TAB_STYLE, selected_style=TAB_SELECTED),
                        dcc.Tab(label='Notas em Aberto',value='tab-notas-aberto',
                                style=TAB_STYLE, selected_style=TAB_SELECTED),
                    ],
                ),
            ],
        ),

        # ── Main content ──────────────────────────────────────────────────────
        dcc.Loading(
            children=html.Div(id='tabs-content', style={'padding': '28px 32px'}),
            fullscreen=True,
            overlay_style={
                'visibility': 'visible',
                'opacity': 1,
                'backgroundColor': C_BG,
            },
            custom_spinner=html.Div([
                dbc.Spinner(color=C_PURPLE, size='lg'),
                html.P('Carregando...', style={
                    'color': C_PURPLE, 'marginTop': '16px',
                    'fontSize': '15px', 'fontWeight': '600',
                    'fontFamily': FONT,
                }),
            ], style={
                'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
            }),
        ),

        # ── Filter sidebar ────────────────────────────────────────────────────
        dbc.Offcanvas(
            id='sidebar-filters',
            title='Filtros',
            is_open=False,
            placement='end',
            style={
                'backgroundColor': C_WHITE,
                'fontFamily': FONT,
                'width': '340px',
            },
            children=[
                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'},
                    children=[
                        # Date
                        html.Div([
                            html.Label('Período', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.DatePickerRange(
                                id='filter-date',
                                start_date='2025-01-01',
                                end_date=datetime.now().strftime('%Y-%m-%d'),
                                style={'width': '100%'},
                            ),
                        ]),
                        # Granularity
                        html.Div([
                            html.Label('Granularidade', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(
                                id='filter-grain',
                                options=[
                                    {'label': 'Diário',   'value': 'day'},
                                    {'label': 'Semanal',  'value': 'week'},
                                    {'label': 'Mensal',   'value': 'month'},
                                ],
                                value='month', clearable=False,
                            ),
                        ]),
                        # Doc type
                        html.Div([
                            html.Label('Tipo de Documento', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(id='filter-doc', multi=True,
                                         placeholder='Todos'),
                        ]),
                        # Status
                        html.Div([
                            html.Label('Status', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(
                                id='filter-status',
                                options=['CAPTURE', 'MAILBOX_CAPTURE',
                                         'INTERNAL_USER', 'EXTERNAL_USER'],
                                placeholder='Todos',
                            ),
                        ]),
                        # Fluxo
                        html.Div([
                            html.Label('Fluxo', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(id='filter-fluxo', multi=True,
                                         placeholder='Todos'),
                        ]),
                        # Tomador
                        html.Div([
                            html.Label('CNPJ Tomador', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(id='filter-tomador', multi=True,
                                         placeholder='Todos'),
                        ]),
                        # Fornecedor
                        html.Div([
                            html.Label('CNPJ Fornecedor', style={
                                'fontSize': '12px', 'fontWeight': '600',
                                'color': C_GRAY, 'textTransform': 'uppercase',
                                'letterSpacing': '0.05em', 'marginBottom': '6px',
                                'display': 'block',
                            }),
                            dcc.Dropdown(id='filter-fornecedor', multi=True,
                                         placeholder='Todos'),
                        ]),
                        # Apply button
                        html.Button(
                            'Aplicar Filtros',
                            id='btn-apply',
                            n_clicks=0,
                            style={
                                'width': '100%',
                                'backgroundColor': C_PURPLE,
                                'color': C_WHITE,
                                'border': 'none',
                                'borderRadius': '8px',
                                'padding': '12px',
                                'fontSize': '14px',
                                'fontWeight': '700',
                                'fontFamily': FONT,
                                'cursor': 'pointer',
                                'marginTop': '8px',
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

# Clear content immediately on tab/filter click (before server responds)
app.clientside_callback(
    'function(tab, n) { return null; }',
    Output('tabs-content', 'children', allow_duplicate=True),
    Input('tabs', 'value'),
    Input('btn-apply', 'n_clicks'),
    prevent_initial_call=True,
)


@app.callback(
    Output('sidebar-filters', 'is_open'),
    Input('open-filters', 'n_clicks'),
    State('sidebar-filters', 'is_open'),
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
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
    State('filter-grain', 'value'),
)
def render_content(tab, n_clicks, search, start, end,
                   doc_types, status, fluxo, tomador, fornecedor, grain):
    customer_id   = get_customer_from_search(search)
    filters       = build_filters(start, end, doc_types, status, fluxo, tomador, fornecedor)
    filters_tuple = tuple(tuple(d.items()) for d in filters)
    pd_grain      = {'day': 'D', 'week': 'W', 'month': 'ME'}.get(grain, 'ME')

    if tab == 'tab-resumo':
        return layouts.get_resumo_iframe(HTML_HOMEPAGE_CONTENT)

    if tab == 'tab-captura':
        return layouts.get_captura_layout(
            pd_grain, get_cached_captura_data(grain, customer_id, filters_tuple), grain,
        )

    if tab == 'tab-divergencia':
        return layouts.get_divergencia_layout(
            pd_grain, get_cached_divergencia_data(grain, customer_id, filters_tuple), grain,
        )

    if tab == 'tab-notas-aberto':
        return layouts.get_notas_aberto_layout(
            pd_grain, get_cached_notas_aberto_data(grain, customer_id, filters_tuple), grain,
        )

    return html.Div('Conteúdo não encontrado.', style={'color': C_GRAY, 'fontFamily': FONT})


@app.callback(
    [Output('tabela-analitica-captura', 'data'),
     Output('tabela-analitica-captura', 'columns')],
    [Input('tabela-analitica-captura', 'page_current'),
     Input('tabela-analitica-captura', 'page_size'),
     Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'),
     State('filter-date', 'end_date'), State('filter-doc', 'value'),
     State('filter-status', 'value'), State('filter-fluxo', 'value'),
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'),
     State('url', 'search')],
)
def update_captura_table(*args):
    return fetch_table_data(*args)


@app.callback(
    [Output('tabela-analitica-divergencias', 'data'),
     Output('tabela-analitica-divergencias', 'columns')],
    [Input('tabela-analitica-divergencias', 'page_current'),
     Input('tabela-analitica-divergencias', 'page_size'),
     Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'),
     State('filter-date', 'end_date'), State('filter-doc', 'value'),
     State('filter-status', 'value'), State('filter-fluxo', 'value'),
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'),
     State('url', 'search')],
)
def update_divergencia_table(*args):
    return fetch_table_data(*args)


@app.callback(
    [Output('tabela-analitica-notas-aberto', 'data'),
     Output('tabela-analitica-notas-aberto', 'columns')],
    [Input('tabela-analitica-notas-aberto', 'page_current'),
     Input('tabela-analitica-notas-aberto', 'page_size'),
     Input('btn-apply', 'n_clicks')],
    [State('tabs', 'value'), State('filter-date', 'start_date'),
     State('filter-date', 'end_date'), State('filter-doc', 'value'),
     State('filter-status', 'value'), State('filter-fluxo', 'value'),
     State('filter-tomador', 'value'), State('filter-fornecedor', 'value'),
     State('url', 'search')],
)
def update_notas_aberto_table(*args):
    return fetch_table_data(*args)


@app.callback(
    Output('filter-fluxo',     'options'),
    Output('filter-fornecedor','options'),
    Output('filter-tomador',   'options'),
    Output('filter-doc',       'options'),
    Input('tabs', 'value'),
    Input('url', 'search'),
)
def load_dropdown_options(tab, search):
    customer_id = get_customer_from_search(search)
    options     = get_cached_filter_options(customer_id)
    return (
        options.get('fluxos', []),
        options.get('fornecedores', []),
        options.get('tomadores', []),
        ['Vinvoice::MaterialInvoice', 'Vinvoice::ServiceInvoice'],
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
