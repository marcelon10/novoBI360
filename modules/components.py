from dash import html, dcc

# ── Brand tokens ──────────────────────────────────────────────────────────────
FONT           = 'Ubuntu, sans-serif'
C_PURPLE       = '#592a9e'
C_PURPLE_LIGHT = '#783dbc'
C_ORANGE       = '#e16500'
C_NAVY         = '#151731'
C_GRAY         = '#6b7280'
C_GRAY_LIGHT   = '#e5e7eb'
C_WHITE        = '#ffffff'
C_RED          = '#ef4444'


# ── Reusable building blocks ──────────────────────────────────────────────────

def kpi_card(title, value, icon_class, color):
    """White card with coloured icon, large metric value and a 'Ver detalhes' link."""
    return html.Div(
        style={
            'backgroundColor': C_WHITE,
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
            'border': f'1px solid {C_GRAY_LIGHT}',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '10px',
            'flex': '1',
            'minWidth': '0',
        },
        children=[
            html.P(title, style={
                'margin': 0,
                'fontSize': '13px',
                'color': C_GRAY,
                'fontFamily': FONT,
                'fontWeight': '500',
            }),
            html.Div(
                style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                children=[
                    html.Span(
                        html.I(className=icon_class),
                        style={
                            'backgroundColor': color + '1a',   # ~10 % opacity
                            'color': color,
                            'width': '36px',
                            'height': '36px',
                            'borderRadius': '50%',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'fontSize': '15px',
                            'flexShrink': '0',
                        },
                    ),
                    html.H2(
                        str(value),
                        style={
                            'margin': 0,
                            'fontSize': '26px',
                            'fontWeight': '700',
                            'color': C_NAVY,
                            'fontFamily': FONT,
                            'lineHeight': '1',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'whiteSpace': 'nowrap',
                        },
                    ),
                ],
            ),
            html.Span('Ver detalhes →', style={
                'color': C_PURPLE,
                'fontSize': '12px',
                'fontFamily': FONT,
                'cursor': 'default',
                'marginTop': '2px',
            }),
        ],
    )


def chart_card(title, children):
    """White card wrapper used around every chart/table in the grid."""
    return html.Div(
        style={
            'backgroundColor': C_WHITE,
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
            'border': f'1px solid {C_GRAY_LIGHT}',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '12px',
        },
        children=[
            html.Div(
                style={'display': 'flex', 'flexDirection': 'column', 'gap': '2px'},
                children=[
                    html.H3(title, style={
                        'margin': 0,
                        'fontSize': '14px',
                        'fontWeight': '600',
                        'color': C_NAVY,
                        'fontFamily': FONT,
                    }),
                    html.Span('Ver detalhes →', style={
                        'color': C_PURPLE,
                        'fontSize': '12px',
                        'fontFamily': FONT,
                        'cursor': 'default',
                    }),
                ],
            ),
            children,
        ],
    )


def section_title(text):
    return html.H2(text, style={
        'margin': '0 0 16px 0',
        'fontSize': '18px',
        'fontWeight': '700',
        'color': C_NAVY,
        'fontFamily': FONT,
    })


# ── Legacy KPI blocks (kept so layouts.py still works) ────────────────────────

def create_captura_kpi_layout(data):
    total    = data.get('totalCount', 0)
    auto     = data.get('autoCount', 0)
    manual   = total - auto
    auto_pct = (auto / total * 100) if total > 0 else 0

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '12px'},
        children=[
            kpi_card('Total de Notas',         f"{total:,}".replace(',', '.'),  'fas fa-file-invoice',  C_PURPLE),
            kpi_card('Ingresso Automático',    f"{auto_pct:.1f}%",              'fas fa-bolt',          C_ORANGE),
            kpi_card('Ingresso Manual',        f"{manual:,}".replace(',', '.'), 'fas fa-hand-paper',    C_GRAY),
        ],
    )


def create_divergencia_kpi_layout(data):
    total   = data.get('totalCount', 0)
    com_div = data.get('totalComDivergencia', 0)
    pct     = (com_div / total * 100) if total > 0 else 0

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '12px'},
        children=[
            kpi_card('Total de Notas',    f"{total:,}".replace(',', '.'),   'fas fa-file-invoice',        C_PURPLE),
            kpi_card('Taxa Divergência',  f"{pct:.1f}%",                   'fas fa-exclamation-triangle', C_RED),
            kpi_card('Com Divergência',   f"{com_div:,}".replace(',', '.'), 'fas fa-times-circle',         C_RED),
        ],
    )


def create_notas_aberto_kpi_layout(data):
    total    = data.get('totalEmAberto', 0)
    humanas  = data.get('totalEmAbertoHumanas', 0)
    sistemas = total - humanas
    pct      = (humanas / total * 100) if total > 0 else 0

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '12px'},
        children=[
            kpi_card('Total em Aberto',    f"{total:,}".replace(',', '.'),    'fas fa-clock',  C_ORANGE),
            kpi_card('Interação Humana',   f"{pct:.1f}%",                    'fas fa-user',   C_RED),
            kpi_card('Pendência Sistema',  f"{sistemas:,}".replace(',', '.'), 'fas fa-robot',  C_PURPLE),
        ],
    )


def create_filter_box(title, options, placeholder, component_id=None):
    return html.Div(
        style={'marginBottom': '16px'},
        children=[
            html.P(title, style={
                'fontWeight': '600',
                'marginBottom': '6px',
                'color': C_NAVY,
                'fontSize': '13px',
                'fontFamily': FONT,
            }),
            dcc.Dropdown(
                id=component_id,
                options=options,
                placeholder=placeholder,
                style={'fontSize': '13px'},
            ),
        ],
    )
