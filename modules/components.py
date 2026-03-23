from dash import html, dcc
import dash_bootstrap_components as dbc


def create_captura_kpi_layout(data):

    total_invoices = data.get("totalCount", 0)
    automatic_invoices = data.get("autoCount", 0)
    manual_invoices = total_invoices - automatic_invoices
    auto_pct = (automatic_invoices / total_invoices * 100) if total_invoices > 0 else 0

    return html.Div(
        style={
            "backgroundColor": "#1f2937",
            "borderRadius": "8px",
            "padding": "20px",
            "textAlign": "center",
            "height": "100%",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-around",
        },
        children=[
            html.Div(
                [
                    html.H2(
                        f"{total_invoices:,}".replace(",", "."),
                        style={
                            "margin": "0",
                            "color": "#8B5CF6",
                            "fontSize": "3em",
                            "fontWeight": "900",
                        },
                    ),
                    html.P(
                        "Notas Ingressadas no Período",
                        style={"margin": "0", "color": "#9ca3af", "fontSize": "1em"},
                    ),
                ]
            ),
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-around",
                    "alignItems": "center",
                    "margin": "20px 0",
                },
                children=[
                    html.Div(
                        [
                            html.P(
                                f"{automatic_invoices:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Capturadas Automaticamente",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                f"{manual_invoices:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Ingressadas Manualmente",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                [
                    html.H3(
                        f"{auto_pct:.0f}%",
                        style={
                            "margin": "0",
                            "color": "#00b894",
                            "fontSize": "2.5em",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        "de automatismo no ingresso de notas",
                        style={"margin": "0", "color": "#9ca3af"},
                    ),
                ]
            ),
        ],
    )
    
def create_divergencia_kpi_layout(data):

    total_notas = data.get("totalCount", 0)
    notas_com_divergencia = data.get("totalComDivergencia", 0)
    notas_sem_divergencia = total_notas - notas_com_divergencia
    auto_pct = (notas_com_divergencia / total_notas * 100) if total_notas > 0 else 0

    return html.Div(
        style={
            "backgroundColor": "#1f2937",
            "borderRadius": "8px",
            "padding": "20px",
            "textAlign": "center",
            "height": "100%",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-around",
        },
        children=[
            html.Div(
                [
                    html.H2(
                        f"{total_notas:,}".replace(",", "."),
                        style={
                            "margin": "0",
                            "color": "#8B5CF6",
                            "fontSize": "3em",
                            "fontWeight": "900",
                        },
                    ),
                    html.P(
                        "Notas Ingressadas no Período",
                        style={"margin": "0", "color": "#9ca3af", "fontSize": "1em"},
                    ),
                ]
            ),
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-around",
                    "alignItems": "center",
                    "margin": "20px 0",
                },
                children=[
                    html.Div(
                        [
                            html.P(
                                f"{notas_com_divergencia:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Notas com Divergência",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                f"{notas_sem_divergencia:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Notas sem Divergência",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                [
                    html.H3(
                        f"{auto_pct:.0f}%",
                        style={
                            "margin": "0",
                            "color": "#00b894",
                            "fontSize": "2.5em",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        "de Divergência",
                        style={"margin": "0", "color": "#9ca3af"},
                    ),
                ]
            ),
        ],
    )


def create_filter_box(title, options, placeholder, component_id=None):
    return html.Div(
        [
            html.P(
                title,
                style={
                    "fontWeight": "bold",
                    "marginBottom": "5px",
                    "color": "#d1d5db",
                    "fontSize": "0.9em",
                },
            ),
            dcc.Dropdown(
                id=component_id,
                options=options,
                placeholder=placeholder,
                className="dark-dropdown",
            ),
        ],
        style={"padding": "10px"},
    )

def create_notas_aberto_kpi_layout(data):
    total_em_aberto = data.get("totalEmAberto", 0)
    total_humanas = data.get("totalEmAbertoHumanas", 0)
    total_sistemas = total_em_aberto - total_humanas
    human_pct = (total_humanas / total_em_aberto * 100) if total_em_aberto > 0 else 0

    return html.Div(
        style={
            "backgroundColor": "#1f2937",
            "borderRadius": "8px",
            "padding": "20px",
            "textAlign": "center",
            "height": "100%",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-around",
        },
        children=[
            html.Div(
                [
                    html.H2(
                        f"{total_em_aberto:,}".replace(",", "."),
                        style={
                            "margin": "0",
                            "color": "#F59E0B",
                            "fontSize": "3em",
                            "fontWeight": "900",
                        },
                    ),
                    html.P(
                        "Notas em Aberto",
                        style={"margin": "0", "color": "#9ca3af", "fontSize": "1em"},
                    ),
                ]
            ),
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-around",
                    "alignItems": "center",
                    "margin": "20px 0",
                },
                children=[
                    html.Div(
                        [
                            html.P(
                                f"{total_humanas:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Pendentes Humanos",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                f"{total_sistemas:,}".replace(",", "."),
                                style={
                                    "fontSize": "2em",
                                    "fontWeight": "bold",
                                    "color": "#d1d5db",
                                    "margin": "0",
                                },
                            ),
                            html.P(
                                "Pendentes Sistema",
                                style={"color": "#9ca3af", "margin": "0"},
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                [
                    html.H3(
                        f"{human_pct:.0f}%",
                        style={
                            "margin": "0",
                            "color": "#EF4444",
                            "fontSize": "2.5em",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        "de notas paradas com usuários",
                        style={"margin": "0", "color": "#9ca3af"},
                    ),
                ]
            ),
        ],
    )
