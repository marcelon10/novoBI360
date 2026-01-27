import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import layouts

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

tab_style = {'backgroundColor': '#1f2937', 'color': '#d1d5db'}
selected_style = {'backgroundColor': '#8B5CF6', 'color': 'white'}

app.layout = html.Div(style={'backgroundColor': '#111827', 'minHeight': '100vh', 'padding': '20px'}, children=[
    dcc.Location(id='url'),
    dcc.Tabs(id="tabs", value='tab-resumo', children=[
        dcc.Tab(label='Resumo', value='tab-resumo', style=tab_style, selected_style=selected_style),
        dcc.Tab(label='Captura', value='tab-captura', style=tab_style, selected_style=selected_style),
    ]),
    html.Div(id='tabs-content', style={'marginTop': '20px'})
])

@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-resumo':
        from constants import HTML_HOMEPAGE_CONTENT 
        return layouts.get_resumo_iframe(HTML_HOMEPAGE_CONTENT)
    elif tab == 'tab-captura':
        return layouts.get_captura_layout()
    return html.Div("Conteúdo em desenvolvimento", style={'color': 'white'})

if __name__ == '__main__':
    app.run(
        debug=True, 
        host="0.0.0.0", 
        port=8050, 
        dev_tools_ui=True, 
        dev_tools_props_check=True
    )