import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dash_table, html

# ── Brand palette (from design PDF) ──────────────────────────────────────────
C_PURPLE       = '#592a9e'
C_PURPLE_LIGHT = '#783dbc'
C_PURPLE_DARK  = '#391b54'
C_ORANGE       = '#e16500'
C_YELLOW       = '#e2e23f'
C_NAVY         = '#151731'
C_GRAY         = '#6b7280'
C_GRAY_LIGHT   = '#e5e7eb'
C_GREEN        = '#22c55e'
C_RED          = '#ef4444'
C_WHITE        = '#ffffff'

FONT = 'Ubuntu, sans-serif'

# Default bar palette for multi-series charts
BAR_PALETTE = [C_PURPLE, C_ORANGE, C_YELLOW, C_PURPLE_LIGHT, C_GREEN, C_RED]


def _base_layout(title='', margin=None):
    return dict(
        title_text=title,
        title_x=0.5,
        title_font=dict(family=FONT, size=13, color=C_NAVY),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family=FONT, size=11, color=C_GRAY),
        margin=margin or dict(t=10, b=60, l=40, r=20),
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.35,
            xanchor='center', x=0.5,
            font=dict(color=C_GRAY, size=11),
            bgcolor='rgba(0,0,0,0)',
        ),
        hovermode='x unified',
    )


def create_combined_chart(data, bar_keys, line_key=None, bar_colors=None,
                          bar_names=None, line_name=None, line_color=None, title=''):
    if not data:
        return go.Figure().update_layout(
            title='Sem dados disponíveis', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT, color=C_GRAY)
        )

    fig = make_subplots(specs=[[{'secondary_y': line_key is not None}]])
    x_axis = [d.get('display_date', 'N/A') for d in data]

    for i, key in enumerate(bar_keys):
        name  = bar_names[i]  if bar_names  else key
        color = bar_colors[i] if bar_colors else BAR_PALETTE[i % len(BAR_PALETTE)]
        fig.add_trace(
            go.Bar(
                x=x_axis, y=[d.get(key, 0) for d in data],
                name=name, marker_color=color, marker_line_width=0,
            ),
            secondary_y=False,
        )

    if line_key:
        fig.add_trace(
            go.Scatter(
                x=x_axis, y=[d.get(line_key, 0) for d in data],
                name=line_name or 'Percentual',
                mode='lines+markers',
                line=dict(color=line_color or C_ORANGE, width=2),
                marker=dict(size=5, color=line_color or C_ORANGE),
            ),
            secondary_y=True,
        )

    layout = _base_layout(title)
    layout['barmode'] = 'stack'
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=False, linecolor=C_GRAY_LIGHT, color=C_GRAY)
    fig.update_yaxes(showgrid=True, gridcolor=C_GRAY_LIGHT, zeroline=False,
                     secondary_y=False, color=C_GRAY)
    if line_key:
        fig.update_yaxes(showgrid=False, zeroline=False, secondary_y=True,
                         ticksuffix='%', range=[0, 105], color=C_GRAY)
    return fig


def create_pie_chart(labels, values, colors=None, title='', hole=0.45):
    if not labels or not any(v for v in values):
        return go.Figure().update_layout(
            title=title, paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT, color=C_GRAY)
        )

    colors = colors or BAR_PALETTE[:len(labels)]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=hole,
        marker=dict(colors=colors, line=dict(color=C_WHITE, width=2)),
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>%{value:,}<br>%{percent}<extra></extra>',
    )])
    layout = _base_layout(title)
    layout['showlegend'] = True
    layout['margin'] = dict(t=10, b=60, l=10, r=10)
    fig.update_layout(**layout)
    return fig


def create_table_chart(data, col_label, label_key, total_key, auto_key, title=''):
    if not data:
        return go.Figure().update_layout(
            title='Sem dados', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT, color=C_GRAY)
        )

    labels = [str(d.get(label_key, 'N/A')) for d in data]
    totals = [f"{d.get(total_key, 0):,}".replace(',', '.') for d in data]
    pcts   = []
    for d in data:
        t = d.get(total_key, 0)
        a = d.get(auto_key, 0)
        pcts.append(f"{((t - a) / t * 100):.1f}%" if t > 0 else '0.0%')

    row_fill = ['#f5f3ff' if i % 2 == 0 else C_WHITE for i in range(len(labels))]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f'<b>{col_label}</b>', '<b>Volume</b>', '<b>% Manual</b>'],
            fill_color=C_PURPLE,
            align='left',
            font=dict(color=C_WHITE, size=12, family=FONT),
            height=36,
            line_color=C_WHITE,
        ),
        cells=dict(
            values=[labels, totals, pcts],
            fill_color=[row_fill, row_fill, row_fill],
            align='left',
            font=dict(color=C_NAVY, size=12, family=FONT),
            height=32,
            line_color=C_GRAY_LIGHT,
        ),
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def create_analytic_table(id, data, columns):
    return html.Div(
        style={
            'backgroundColor': C_WHITE,
            'borderRadius': '12px',
            'padding': '24px',
            'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
            'border': f'1px solid {C_GRAY_LIGHT}',
        },
        children=[
            html.H3('Tabela Analítica', style={
                'margin': '0 0 16px 0', 'fontSize': '15px', 'fontWeight': '600',
                'color': C_NAVY, 'fontFamily': FONT,
            }),
            dash_table.DataTable(
                id=id,
                columns=columns,
                data=data,
                page_current=0,
                page_size=10,
                page_action='custom',
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': C_PURPLE,
                    'color': C_WHITE,
                    'fontWeight': '600',
                    'border': 'none',
                    'fontFamily': FONT,
                    'fontSize': '13px',
                    'padding': '12px 16px',
                },
                style_cell={
                    'backgroundColor': C_WHITE,
                    'color': C_NAVY,
                    'padding': '10px 16px',
                    'fontFamily': FONT,
                    'border': f'1px solid {C_GRAY_LIGHT}',
                    'textAlign': 'left',
                    'fontSize': '13px',
                },
                style_data_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f5f3ff',
                }],
                style_as_list_view=True,
            ),
        ],
    )


def create_percent_stacked_bar(data, x_key, bar_keys, bar_names=None,
                                bar_colors=None, title=''):
    if not data:
        return go.Figure().update_layout(
            title='Sem dados', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT, color=C_GRAY)
        )

    colors = bar_colors or BAR_PALETTE
    fig = go.Figure()
    for i, key in enumerate(bar_keys):
        name  = bar_names[i] if bar_names else key
        color = colors[i % len(colors)]
        fig.add_trace(go.Bar(
            name=name,
            x=[d.get(x_key) for d in data],
            y=[d.get(key, 0) for d in data],
            marker_color=color, marker_line_width=0,
            hovertemplate=f'<b>%{{x}}</b><br>{name}: %{{y:.1f}}%<extra></extra>',
        ))

    layout = _base_layout(title)
    layout['barmode'] = 'stack'
    fig.update_layout(**layout)
    fig.update_yaxes(ticksuffix='%', range=[0, 100],
                     showgrid=True, gridcolor=C_GRAY_LIGHT)
    fig.update_xaxes(showgrid=False)
    return fig


def create_delta_line_chart(data, line_keys, line_names=None,
                             line_colors=None, title=''):
    if not data:
        return go.Figure().update_layout(
            title='Sem dados disponíveis', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=FONT, color=C_GRAY)
        )

    colors = line_colors or BAR_PALETTE
    fig = go.Figure()
    x_axis = [d.get('display_date', d.get('date', 'N/A')) for d in data]

    for i, key in enumerate(line_keys):
        name  = line_names[i] if line_names else key
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=x_axis, y=[d.get(key, 0) for d in data],
            name=name, mode='lines+markers',
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>%{{x}}</b><br>{name}: %{{y:,}}<extra></extra>',
        ))

    layout = _base_layout(title)
    layout['hovermode'] = 'x unified'
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=False, zeroline=False, color=C_GRAY)
    fig.update_yaxes(showgrid=True, gridcolor=C_GRAY_LIGHT, zeroline=False, color=C_GRAY)
    return fig
