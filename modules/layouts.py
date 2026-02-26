import pandas as pd
from dash import html, dcc
import api_client
import charting
import components

def aggregate_by_grain(data, date_col='date', sum_cols=None, grain='ME'):
    if not data:
        return []
    
    sum_cols = sum_cols or []
    df = pd.DataFrame(data)
    df[date_col] = pd.to_datetime(df[date_col]) 
    
    agg_map = {col: 'sum' for col in sum_cols}
    resampled = df.set_index(date_col).resample(grain).agg(agg_map).reset_index()
    
    date_formats = {
        'ME': '%b %Y',
        'W': 'W%U %Y',
        'D': '%d/%m/%y'
    }
    fmt = date_formats.get(grain, '%d/%m/%y')
    resampled['display_date'] = resampled[date_col].dt.strftime(fmt)
        
    return resampled.to_dict('records')

def get_captura_layout(selected_grain='ME', filters=None, api_grain='month'):
    # 1. Busca os dados na API
    captura_data = api_client.get_captura(filters=filters, customer='aegea_prod', grain=api_grain)
    captura_fornecedores_data = api_client.get_captura_fornecedores(filters=filters, customer='aegea_prod')
    captura_cidades_data = api_client.get_captura_cidades(filters=filters, customer='aegea_prod')
    
    if not captura_data:
        return html.Div("Sem dados para os filtros selecionados", 
                        style={'color': 'white', 'padding': '20px', 'textAlign': 'center'})

    # 2. KPIs e Processamento
    total_val = sum(d.get('totalCount', 0) for d in captura_data)
    auto_val = sum(d.get('totalAuto', 0) for d in captura_data)
    
    chart_data_geral = aggregate_by_grain(captura_data, sum_cols=['totalCount', 'totalAuto'], grain=selected_grain)
    for row in chart_data_geral:
        row['manualCount'] = row['totalCount'] - row['totalAuto']
        row['autoPct'] = (row['totalAuto'] / row['totalCount'] * 100) if row['totalCount'] > 0 else 0

    # 3. Processamento Story 2
    type_totals = {}
    time_type_map = {}
    for d in captura_data:
        dt = d['date']; t = d.get('documentType', 'N/A'); count = d.get('totalCount', 0)
        type_totals[t] = type_totals.get(t, 0) + count
        if dt not in time_type_map: time_type_map[dt] = {'date': dt}
        time_type_map[dt][t] = time_type_map[dt].get(t, 0) + count

    pie_labels = list(type_totals.keys()); pie_values = list(type_totals.values())
    stacked_data = aggregate_by_grain(list(time_type_map.values()), sum_cols=pie_labels, grain=selected_grain)

    # --- CONFIGURAÇÃO DE ALTURA PADRÃO ---
    GRAPH_HEIGHT = "400px"

    # --- AJUSTE STORY 1 ---
    fig_geral = charting.create_combined_chart(
        chart_data_geral, 
        bar_keys=['totalAuto', 'manualCount'], 
        line_key='autoPct',
        bar_colors=['#8B5CF6', '#374151'], 
        bar_names=['Automático', 'Manual'],
        title=f'Volume Total vs % Automação ({selected_grain})'
    ).update_layout(
        legend=dict(
            orientation="h", 
            yanchor="top",
            y=-0.15,      # Puxado para cima para acompanhar a altura menor
            xanchor="center", 
            x=0.5
        ),
        margin=dict(t=60, b=80, l=40, r=40), 
        title=dict(y=0.98, x=0.5, xanchor='center')
    )

    # --- AJUSTE STORY 2 ---
    fig_stacked = charting.create_combined_chart(
        stacked_data, 
        bar_keys=pie_labels, 
        bar_names=pie_labels,
        title='Composição por Tipo de Documento (Temporal)'
    ).update_layout(
        barmode='stack',
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=60, b=80, l=40, r=40),
        title=dict(y=0.98, x=0.5, xanchor='center')
    )

    # --- MONTAGEM DO LAYOUT ---
    story1 = html.Div(style={'marginBottom': '20px'}, children=[
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 2.5fr', 'gap': '20px'}, children=[
            components.create_captura_kpi_layout({'totalCount': total_val, 'autoCount': auto_val}),
            dcc.Graph(figure=fig_geral, style={"height": GRAPH_HEIGHT}) 
        ])
    ])

    story2 = html.Div(style={'backgroundColor': '#1f2937', 'padding': '20px', 'borderRadius': '8px'}, children=[
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1.5fr 1fr', 'gap': '20px'}, children=[
            dcc.Graph(figure=fig_stacked, style={"height": GRAPH_HEIGHT}), 
            dcc.Graph(figure={
                'data': [{'labels': pie_labels, 'values': pie_values, 'type': 'pie', 'hole': .4}],
                'layout': {
                    'template': 'plotly_dark', 
                    'title': 'Composição (Percentual)',
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'showlegend': False,
                    'legend': {'orientation': 'h', 'y': -0.15, 'x': 0.5, 'xanchor': 'center'},
                    'margin': {'t': 60, 'b': 80, 'l': 20, 'r': 20}
                }
            }, style={"height": GRAPH_HEIGHT})
        ])
    ])
    
    story3 = html.Div(style={'marginBottom': '20px'}, children=[
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
                # Tabela de Fornecedores
                dcc.Graph(
                    figure=charting.create_table_chart(
                        data=captura_fornecedores_data, 
                        col_label="Fornecedor (CNPJ)", 
                        label_key="supplierCnpj", # Chave exata da sua classe Captura no GraphQL
                        total_key="totalCount",
                        auto_key="totalAuto",
                        title="Top 10 Fornecedores por Volume"
                    ).update_layout(height=400),
                    style={'height': '400px'}
                ),
                # Tabela de Cidades
                dcc.Graph(
                    figure=charting.create_table_chart(
                        data=captura_cidades_data,
                        col_label="Cidade", 
                        label_key="currency", # Chave exata da sua classe Captura no GraphQL
                        total_key="totalCount",
                        auto_key="totalAuto",
                        title="Top 10 Cidades por Volume"
                    ).update_layout(height=400),
                    style={'height': '400px'}
                )
            ])
        ])
    
    # --- STORY 4 (DETALHAMENTO ANALÍTICO) ---
    # Definimos as colunas que queremos exibir na tabela
    colunas_analiticas = [
        {"name": "ID da Nota", "id": "id"},
        {"name": "CNPJ Fornecedor", "id": "supplierCnpj"},
        {"name": "Data de Emissão", "id": "issueDate"},
        {"name": "Tipo de Ingresso", "id": "provider"},
        {"name": "Valor Total", "id": "totalValue"},
        {"name": "Tipo do Documento", "id": "documentType"}
    ]

    story4 = html.Div(style={'marginTop': '20px'}, children=[
        charting.create_analytic_table(
            id='tabela-analitica', 
            data=[], # Começa vazia, o callback preenche
            columns=colunas_analiticas
        )
    ])

    return html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "20px"},
        children=[story1, story2, story3, story4] # Adicionado story3 aqui
    )
    
def get_resumo_iframe(content):
    return html.Iframe(srcDoc=content, style={'width': '100%', 'height': '2000px', 'border': 'none'})