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