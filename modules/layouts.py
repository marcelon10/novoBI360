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
    # 1. Fetch filtered data from API
    # We pass the filters list received from the app.py callback
    raw_data = api_client.get_captura(filters=filters, grain=api_grain) 
    
    if not raw_data:
        return html.Div("Sem dados para os filtros selecionados", 
                        style={'color': 'white', 'padding': '20px', 'textAlign': 'center'})

    # 2. Big Numbers (KPIs) 
    total_val = sum(d.get('totalCount', 0) for d in raw_data)
    auto_val = sum(d.get('totalAuto', 0) for d in raw_data)
    
    # 3. Flexible Aggregation for the Chart
    chart_data = aggregate_by_grain(
        data=raw_data, 
        sum_cols=['totalCount', 'totalAuto'], 
        grain=selected_grain
    )
    
    # 4. Business Logic (Dash-side math)
    for row in chart_data:
        row['manualCount'] = row.get('totalCount', 0) - row.get('totalAuto', 0)
        if row.get('totalCount', 0) > 0:
            row['autoPct'] = (row.get('totalAuto', 0) / row.get('totalCount', 0)) * 100
        else:
            row['autoPct'] = 0
    
    # 5. Return the Layout
    return html.Div([
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
            components.create_captura_kpi_layout({'totalCount': total_val, 'autoCount': auto_val}),
            
            dcc.Graph(figure=charting.create_combined_chart(
                data=chart_data,
                bar_keys=['totalAuto', 'manualCount'], 
                line_key='autoPct',                     
                bar_colors=['#8B5CF6', '#374151'],      
                bar_names=['Automático', 'Manual'],
                line_name='% Automatismo',
                line_color='#10B981',
                title=f'Ingresso de Notas: Automático vs Manual ({selected_grain})'
            ))
        ])
    ])

def get_resumo_iframe(content):
    return html.Iframe(srcDoc=content, style={'width': '100%', 'height': '2000px', 'border': 'none'})