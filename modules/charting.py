import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def create_table_chart(data, col_name, title=""):
    if not data:
        return go.Figure()

    # Extraindo colunas
    labels = [d['label'] for d in data[:10]]
    totals = [f"{d['total']:,}".replace(",", ".") for d in data[:10]]
    pcts = [f"{d['pct']:.1f}%" for d in data[:10]]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f'<b>{col_name}</b>', '<b>Total</b>', '<b>% Auto</b>'],
            fill_color='#1f2937',
            align='left',
            font=dict(color='white', size=13),
            height=35
        ),
        cells=dict(
            values=[labels, totals, pcts],
            fill_color='rgba(0,0,0,0)', # Fundo transparente para casar com o story
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
        font=dict(family="Inter, sans-serif", color="#d1d5db"),
        height=350 # Altura fixa para alinhar com os outros gráficos
    )
    return fig