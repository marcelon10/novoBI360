import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dash_table, html

def create_combined_chart(data, bar_keys, line_key=None, bar_colors=None, bar_names=None, line_name=None, line_color=None, title=""):
    if not data:
        return go.Figure().update_layout(title="Sem dados disponíveis", template="plotly_dark")
    
    # Enable secondary Y axis only if line_key is provided
    fig = make_subplots(specs=[[{"secondary_y": line_key is not None}]])
    
    x_axis = [d.get('display_date', 'N/A') for d in data]
    
    # 1. Add Bars (this will stack if bar_keys has more than one item)
    for i, key in enumerate(bar_keys):
        name = bar_names[i] if bar_names else key
        color = bar_colors[i] if bar_colors else None
        fig.add_trace(
            go.Bar(x=x_axis, y=[d.get(key, 0) for d in data], name=name, marker_color=color),
            secondary_y=False
        )

    # 2. Add Line (Optional)
    if line_key:
        fig.add_trace(
            go.Scatter(
                x=x_axis, y=[d.get(line_key, 0) for d in data],
                name=line_name or "Percentual",
                mode='lines+markers',
                line=dict(color=line_color or '#10B981', width=3)
            ),
            secondary_y=True
        )

    fig.update_layout(
        barmode='stack', # Ensures bars are stacked
        title_text=title,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#d1d5db')),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db"),
        template="plotly_dark"
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, secondary_y=False)
    if line_key:
        fig.update_yaxes(showgrid=False, secondary_y=True, range=[0, 105])
        
    return fig

def create_pie_chart(labels, values, colors, title, hole=0.3):

    fig = go.Figure(
        data=[go.Pie(labels=labels, values=values, hole=hole, marker_colors=colors)]
    )

    fig.update_traces(textinfo="percent+label", pull=[0.05] * len(labels))

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db"),
    )

    return fig

def create_table_chart(data, col_label, label_key, total_key, auto_key, title=""):
    if not data:
        return go.Figure().update_layout(title="Sem dados", template="plotly_dark")

    # Extração direta das chaves da API
    labels = [str(d.get(label_key, 'N/A')) for d in data]
    totals = [f"{d.get(total_key, 0):,}".replace(",", ".") for d in data]
    
    # Cálculo do % Manual direto na montagem da lista para a tabela
    pcts = []
    for d in data:
        t = d.get(total_key, 0)
        a = d.get(auto_key, 0)
        p = ((t - a) / t * 100) if t > 0 else 0
        pcts.append(f"{p:.1f}%")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f'<b>{col_label}</b>', '<b>Total Notas</b>', '<b>% Manual</b>'],
            fill_color='#111827',
            align='left',
            font=dict(color='#8B5CF6', size=13),
            height=35
        ),
        cells=dict(
            values=[labels, totals, pcts],
            fill_color='#1f2937',
            align='left',
            font=dict(color='#d1d5db', size=12),
            height=30
        ))
    ])

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#d1d5db")
    )
    return fig

def create_analytic_table(id, data, columns):
    """
    id: Identificador único para o callback de paginação
    data: Lista de dicionários vinda da API
    columns: Lista de dicts [{'name': 'CNPJ', 'id': 'supplierCnpj'}, ...]
    """
    return html.Div(style={'backgroundColor': '#1f2937', 'padding': '20px', 'borderRadius': '8px'}, children=[
        dash_table.DataTable(
            id=id,
            columns=columns,
            data=data,
            # --- CONFIGURAÇÃO DE PAGINAÇÃO ---
            page_current=0,
            page_size=10,
            page_action='custom',  # Indica que o Python/API vai processar as páginas
            
            # --- ESTILIZAÇÃO (Combinando com seu Plotly Dark) ---
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': '#111827',
                'color': '#8B5CF6',
                'fontWeight': 'bold',
                'border': '1px solid #374151'
            },
            style_cell={
                'backgroundColor': '#1f2937',
                'color': '#d1d5db',
                'padding': '10px',
                'fontFamily': 'Inter, sans-serif',
                'border': '1px solid #374151',
                'textAlign': 'left'
            },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#111827', # Efeito zebra
            }],
            # Botões de navegação customizados pelo CSS do Dash
            style_as_list_view=True,
        )
    ])

def create_percent_stacked_bar(data, x_key, bar_keys, bar_names=None, bar_colors=None, title=""):
    if not data:
        return go.Figure().update_layout(title="Sem dados", template="plotly_dark")

    fig = go.Figure()

    for i, key in enumerate(bar_keys):
        name = bar_names[i] if bar_names else key
        color = bar_colors[i] if bar_colors else None
        
        fig.add_trace(go.Bar(
            name=name,
            x=[d.get(x_key) for d in data],
            y=[d.get(key, 0) for d in data],
            marker_color=color,
            # Mostra o valor percentual no hover de forma limpa
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y}}%<extra></extra>"
        ))

    fig.update_layout(
        barmode='stack',
        title_text=title,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(ticksuffix="%", range=[0, 100], showgrid=False),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        font=dict(family="Inter, sans-serif", color="#d1d5db"),
        template="plotly_dark",
        margin=dict(t=60, b=80, l=40, r=40)
    )

    return fig

def create_delta_line_chart(data, line_keys, line_names=None, line_colors=None, title=""):
    """
    Cria um gráfico de linhas comparativo temporal.
    line_keys: Lista com as duas chaves para comparar (ex: ['totalCount', 'totalComDivergencia'])
    """
    if not data:
        return go.Figure().update_layout(title="Sem dados disponíveis", template="plotly_dark")
    
    fig = go.Figure()
    
    x_axis = [d.get('display_date', d.get('date', 'N/A')) for d in data]
    
    # Cores padrão caso não sejam enviadas (Roxo e Vermelho/Verde)
    default_colors = ['#8B5CF6', '#EF4444', '#10B981', '#34D399']

    for i, key in enumerate(line_keys):
        name = line_names[i] if line_names else key
        color = line_colors[i] if line_colors else default_colors[i % len(default_colors)]
        
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=[d.get(key, 0) for d in data],
            name=name,
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y}}<extra></extra>"
        ))

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        hovermode="x unified", # Mostra os dois valores ao mesmo tempo no hover
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db"),
        template="plotly_dark",
        margin=dict(t=60, b=80, l=40, r=40)
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#374151', zeroline=False)
        
    return fig