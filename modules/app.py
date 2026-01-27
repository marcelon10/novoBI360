import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import layouts
from constants import HTML_HOMEPAGE_CONTENT
from datetime import datetime

import logging
import sys

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
                    options=['MaterialInvoice'],
                    multi=True,
                    placeholder="Selecione...",
                    className="dark-dropdown"
                ),
                
                html.P("Status", className="mt-4 mb-1"),
                dcc.Dropdown(
                    id='filter-status',
                    options=['Automático', 'Manual', 'Email'],
                    placeholder="Selecione...",
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
    State('filter-status', 'value')
)
def render_content(tab, n_clicks, start, end, doc_types, status):
    api_filters = []
    if start: api_filters.append({'field': 'process_created_at', 'value': start, 'operator': 'gte'})
    if end:   api_filters.append({'field': 'process_created_at', 'value': end, 'operator': 'lte'})
    if doc_types: api_filters.append({'field': 'document_type', 'value': ", ".join([f"'{item}'" for item in doc_types]), 'operator': 'in'})
    if status: api_filters.append({'field': 'captura_status', 'value': status, 'operator': 'eq'})

    if tab == 'tab-resumo':
        return layouts.get_resumo_iframe(HTML_HOMEPAGE_CONTENT)
    elif tab == 'tab-captura':
        return layouts.get_captura_layout(filters=api_filters)
    return html.Div("Conteúdo em desenvolvimento", style={'color': 'white'})

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