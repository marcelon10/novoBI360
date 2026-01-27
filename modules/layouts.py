import pandas as pd
from dash import html, dcc
import api_client
import charting
import components

def aggregate_by_grain(data, date_col='date', sum_cols=None, grain='ME'):
    if not data:
        return []
    
    # Default to empty list if no columns provided
    sum_cols = sum_cols or []
    
    df = pd.DataFrame(data)
    df[date_col] = pd.to_datetime(df[date_col]) 
    
    # Dynamically build the aggregation dictionary
    agg_map = {col: 'sum' for col in sum_cols}
    
    resampled = df.set_index(date_col).resample(grain).agg(agg_map).reset_index()
    
    # Logic to handle date formatting based on grain
    date_formats = {
        'ME': '%b %Y',    # Monthly
        'W': 'W%U %Y',    # Weekly
        'D': '%d/%m/%y'   # Daily
    }
    fmt = date_formats.get(grain, '%d/%m/%y')
    resampled['display_date'] = resampled[date_col].dt.strftime(fmt)
        
    return resampled.to_dict('records')

def get_captura_layout(selected_grain='ME'):
    # 1. Fetch raw data from API
    raw_data = api_client.get_captura() 
    
    if not raw_data:
        return html.Div("Sem dados", style={'color': 'white'})

    # 2. Big Numbers (KPIs) - Total of the entire dataset
    # We sum the raw data directly for the cards
    total_val = sum(d.get('totalCount', 0) for d in raw_data)
    auto_val = sum(d.get('totalAuto', 0) for d in raw_data)
    
    # 3. Flexible Aggregation for the Chart
    # We tell the function exactly which columns to sum
    chart_data = aggregate_by_grain(
        data=raw_data, 
        sum_cols=['totalCount', 'totalAuto'], 
        grain=selected_grain
    )
    
    # 4. Business Logic (Dash-side math)
    # Now we loop through the aggregated periods to create the stack and line data
    for row in chart_data:
        # Create the 'Manual' stack: Total - Auto
        row['manualCount'] = row.get('totalCount', 0) - row.get('totalAuto', 0)
        
        # Create the Line data: (Auto / Total) * 100
        if row.get('totalCount', 0) > 0:
            row['autoPct'] = (row.get('totalAuto', 0) / row.get('totalCount', 0)) * 100
        else:
            row['autoPct'] = 0
    
    # 5. Return the Layout
    return html.Div([
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
            # KPI Card component using the full totals
            components.create_captura_kpi_layout({'totalCount': total_val, 'autoCount': auto_val}),
            
            # Combined Chart using the aggregated/processed chart_data
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