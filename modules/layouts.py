import pandas as pd
from dash import html, dcc
import charting
import components  # noqa: F401 (used via components.kpi_card etc.)

# ── Brand tokens (mirror charting.py) ────────────────────────────────────────
C_PURPLE = '#592a9e'
C_ORANGE = '#e16500'
C_NAVY   = '#151731'
C_GRAY   = '#6b7280'
C_RED    = '#ef4444'
C_GREEN  = '#22c55e'
C_WHITE  = '#ffffff'
C_BG     = '#f5f3ff'   # very light purple page background
FONT     = 'Ubuntu, sans-serif'
GRAPH_H  = 320          # standard chart height in px


# ── Helpers ───────────────────────────────────────────────────────────────────

def aggregate_by_grain(data, date_col='date', sum_cols=None, grain='ME'):
    if not data:
        return []
    sum_cols = sum_cols or []
    df = pd.DataFrame(data)
    df[date_col] = pd.to_datetime(df[date_col])
    agg_map = {col: 'sum' for col in sum_cols}
    resampled = df.set_index(date_col).resample(grain).agg(agg_map).reset_index()
    fmt = {'ME': '%b %Y', 'W': 'W%U %Y', 'D': '%d/%m/%y'}.get(grain, '%d/%m/%y')
    resampled['display_date'] = resampled[date_col].dt.strftime(fmt)
    return resampled.to_dict('records')


def _chart_card(title, graph_or_component):
    """White rounded card wrapping a Plotly graph or any component."""
    return html.Div(
        style={
            'backgroundColor': C_WHITE,
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
            'border': '1px solid #e5e7eb',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '8px',
        },
        children=[
            html.Div([
                html.H3(title, style={
                    'margin': 0, 'fontSize': '14px', 'fontWeight': '600',
                    'color': C_NAVY, 'fontFamily': FONT,
                }),
                html.Span('Ver detalhes →', style={
                    'color': C_PURPLE, 'fontSize': '12px',
                    'fontFamily': FONT, 'cursor': 'default',
                }),
            ]),
            graph_or_component,
        ],
    )


def _graph(fig, height=GRAPH_H):
    return dcc.Graph(
        figure=fig,
        style={'height': f'{height}px'},
        config={'displayModeBar': False},
    )


def _kpi_row(cards):
    return html.Div(
        style={
            'display': 'grid',
            'gridTemplateColumns': f'repeat({len(cards)}, 1fr)',
            'gap': '16px',
        },
        children=cards,
    )


def _section(title, content):
    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '16px'},
        children=[
            html.H2(title, style={
                'margin': 0, 'fontSize': '16px', 'fontWeight': '700',
                'color': C_NAVY, 'fontFamily': FONT,
            }),
            content,
        ],
    )


def _grid(*children, cols=3):
    return html.Div(
        style={
            'display': 'grid',
            'gridTemplateColumns': f'repeat({cols}, 1fr)',
            'gap': '16px',
        },
        children=list(children),
    )


def _no_data():
    return html.Div(
        'Sem dados para os filtros selecionados.',
        style={
            'color': C_GRAY, 'padding': '40px',
            'textAlign': 'center', 'fontFamily': FONT,
        },
    )


# ── Captura ───────────────────────────────────────────────────────────────────

def get_captura_layout(selected_grain='ME', api_data=None, api_grain=None):
    series     = (api_data or {}).get('series', [])
    suppliers  = (api_data or {}).get('suppliers', [])
    cities     = (api_data or {}).get('cities', [])

    if not series:
        return _no_data()

    total    = sum(d.get('totalCount', 0) for d in series)
    auto     = sum(d.get('totalAuto',  0) for d in series)
    manual   = total - auto
    auto_pct = (auto / total * 100) if total > 0 else 0

    chart_data = aggregate_by_grain(series, sum_cols=['totalCount', 'totalAuto'], grain=selected_grain)
    for r in chart_data:
        r['manualCount'] = r['totalCount'] - r['totalAuto']
        r['autoPct']     = (r['totalAuto'] / r['totalCount'] * 100) if r['totalCount'] > 0 else 0

    # type breakdown for stacked + pie
    type_totals  = {}
    time_type    = {}
    for d in series:
        dt = d['date']; t = d.get('documentType', 'N/A'); c = d.get('totalCount', 0)
        type_totals[t] = type_totals.get(t, 0) + c
        if dt not in time_type:
            time_type[dt] = {'date': dt}
        time_type[dt][t] = time_type[dt].get(t, 0) + c

    pie_labels   = list(type_totals.keys())
    pie_values   = list(type_totals.values())
    stacked_data = aggregate_by_grain(list(time_type.values()), sum_cols=pie_labels, grain=selected_grain)

    fig_volume = charting.create_combined_chart(
        chart_data,
        bar_keys=['totalAuto', 'manualCount'],
        line_key='autoPct',
        bar_colors=[C_PURPLE, '#c4b5fd'],
        bar_names=['Automático', 'Manual'],
    )
    fig_stacked = charting.create_combined_chart(
        stacked_data, bar_keys=pie_labels, bar_names=pie_labels,
    )
    fig_stacked.update_layout(barmode='stack')
    fig_pie = charting.create_pie_chart(pie_labels, pie_values, title='')

    kpi_cards = _kpi_row([
        components.kpi_card('Total de Notas',      f"{total:,}".replace(',', '.'), 'fas fa-file-invoice',  C_PURPLE),
        components.kpi_card('Ingresso Automático', f"{auto_pct:.1f}%",             'fas fa-bolt',          C_ORANGE),
        components.kpi_card('Notas Automáticas',   f"{auto:,}".replace(',', '.'),  'fas fa-robot',         C_PURPLE),
        components.kpi_card('Ingresso Manual',     f"{manual:,}".replace(',', '.'), 'fas fa-hand-paper',   C_GRAY),
    ])

    charts_row1 = _grid(
        _chart_card('Notas por Tipo de Ingresso',          _graph(fig_volume)),
        _chart_card('Composição por Tipo de Documento',    _graph(fig_stacked)),
        _chart_card('Distribuição Percentual',             _graph(fig_pie)),
        cols=3,
    )

    charts_row2 = _grid(
        _chart_card(
            'Top 10 Fornecedores',
            _graph(charting.create_table_chart(
                suppliers, 'Fornecedor', 'supplierCnpj', 'totalCount', 'totalAuto',
            ), height=280),
        ),
        _chart_card(
            'Top 10 Tomadores / Cidades',
            _graph(charting.create_table_chart(
                cities, 'Tomador', 'currency', 'totalCount', 'totalAuto',
            ), height=280),
        ),
        cols=2,
    )

    analytic = charting.create_analytic_table(
        id='tabela-analitica-captura', data=[], columns=[],
    )

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'},
        children=[
            _section('Indicadores de Ingresso', kpi_cards),
            charts_row1,
            charts_row2,
            analytic,
        ],
    )


# ── Divergência ───────────────────────────────────────────────────────────────

def get_divergencia_layout(selected_grain='ME', api_data=None, api_grain='month'):
    series     = (api_data or {}).get('series', [])
    suppliers  = (api_data or {}).get('suppliers', [])
    tipos      = (api_data or {}).get('types', [])

    if not series:
        return _no_data()

    total   = sum(d.get('totalCount', 0) for d in series)
    com_div = sum(d.get('totalComDivergencia', 0) for d in series)
    pct     = (com_div / total * 100) if total > 0 else 0

    chart_data = aggregate_by_grain(series, sum_cols=['totalCount', 'totalComDivergencia'], grain=selected_grain)
    for r in chart_data:
        r['comDivPct'] = (r['totalComDivergencia'] / r['totalCount'] * 100) if r['totalCount'] > 0 else 0

    df_div = pd.DataFrame(series)
    comp_data, pie_labels, pie_values = [], [], []
    if not df_div.empty:
        tg = df_div.groupby('documentType').agg({
            'totalCount': 'sum', 'totalComDivergencia': 'sum',
        }).reset_index()
        tg['Com Divergência (%)'] = (tg['totalComDivergencia'] / tg['totalCount'] * 100).round(2)
        tg['Sem Divergência (%)'] = 100 - tg['Com Divergência (%)']
        pie_df    = tg[tg['totalComDivergencia'] > 0]
        pie_labels = pie_df['documentType'].tolist()
        pie_values = pie_df['totalComDivergencia'].tolist()
        comp_data  = tg.to_dict('records')

    fig_volume = charting.create_combined_chart(
        chart_data,
        bar_keys=['totalComDivergencia', 'totalCount'],
        line_key='comDivPct',
        bar_colors=[C_RED, '#fca5a5'],
        bar_names=['Com Divergência', 'Sem Divergência'],
    )
    fig_comp = charting.create_percent_stacked_bar(
        comp_data, 'documentType',
        ['Com Divergência (%)', 'Sem Divergência (%)'],
        ['Divergente', 'Saudável'],
        [C_RED, C_GREEN],
    )
    fig_pie = charting.create_pie_chart(pie_labels, pie_values, [C_RED, '#fca5a5', '#fde68a'], title='')
    fig_temporal = charting.create_delta_line_chart(
        chart_data, ['totalCount', 'totalComDivergencia'],
        ['Total Processado', 'Com Divergência'],
        [C_PURPLE, C_RED],
    )

    kpi_cards = _kpi_row([
        components.kpi_card('Total de Notas',       f"{total:,}".replace(',', '.'),  'fas fa-file-invoice',        C_PURPLE),
        components.kpi_card('Taxa de Divergência',  f"{pct:.1f}%",                  'fas fa-exclamation-triangle', C_RED),
        components.kpi_card('Notas Divergentes',    f"{com_div:,}".replace(',', '.'), 'fas fa-times-circle',        C_RED),
        components.kpi_card('Notas Saudáveis',      f"{total-com_div:,}".replace(',', '.'), 'fas fa-check-circle', '#22c55e'),
    ])

    charts_row1 = _grid(
        _chart_card('Volume vs % Divergência',                 _graph(fig_volume)),
        _chart_card('Eficiência por Tipo de Documento',        _graph(fig_comp)),
        _chart_card('Composição das Divergências',             _graph(fig_pie)),
        cols=3,
    )

    charts_row2 = _grid(
        _chart_card(
            'Top 10 Fornecedores por Divergência',
            _graph(charting.create_table_chart(
                suppliers, 'Fornecedor', 'supplierCnpj', 'totalCount', 'totalCount',
            ), height=280),
        ),
        _chart_card(
            'Top 10 Tipos de Divergência',
            _graph(charting.create_table_chart(
                tipos, 'Divergência', 'nomeDivergencia', 'totalCount', 'totalCount',
            ), height=280),
        ),
        _chart_card('Evolução Temporal', _graph(fig_temporal)),
        cols=3,
    )

    analytic = charting.create_analytic_table(
        id='tabela-analitica-divergencias', data=[], columns=[],
    )

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'},
        children=[
            _section('Indicadores de Divergências', kpi_cards),
            charts_row1,
            charts_row2,
            analytic,
        ],
    )


# ── Notas em Aberto ───────────────────────────────────────────────────────────

def get_notas_aberto_layout(selected_grain='ME', api_data=None, api_grain='month'):
    series   = (api_data or {}).get('series', [])
    usuarios = (api_data or {}).get('usuarios', [])
    tarefas  = (api_data or {}).get('tarefas', [])

    if not series:
        return _no_data()

    total   = sum(d.get('totalEmAberto', 0) for d in series)
    humanas = sum(d.get('totalEmAbertoHumanas', 0) for d in series)
    sistemas = total - humanas
    pct     = (humanas / total * 100) if total > 0 else 0

    chart_data = aggregate_by_grain(series, sum_cols=['totalEmAberto', 'totalEmAbertoHumanas'], grain=selected_grain)
    for r in chart_data:
        r['totalSistema'] = r['totalEmAberto'] - r['totalEmAbertoHumanas']
        r['humanPct']     = (r['totalEmAbertoHumanas'] / r['totalEmAberto'] * 100) if r['totalEmAberto'] > 0 else 0

    fig_volume = charting.create_combined_chart(
        chart_data,
        bar_keys=['totalEmAbertoHumanas', 'totalSistema'],
        line_key='humanPct',
        bar_colors=[C_RED, C_ORANGE],
        bar_names=['Pendência Humana', 'Pendência Sistema'],
    )
    fig_volume.update_layout(barmode='stack')
    fig_temporal = charting.create_delta_line_chart(
        chart_data, ['totalEmAberto', 'totalEmAbertoHumanas'],
        ['Total Em Aberto', 'Pendente Humano'],
        [C_ORANGE, C_RED],
    )
    fig_pie = charting.create_pie_chart(
        ['Humana', 'Sistema'], [humanas, sistemas], [C_RED, C_ORANGE],
    )

    kpi_cards = _kpi_row([
        components.kpi_card('Total em Aberto',    f"{total:,}".replace(',', '.'),    'fas fa-clock',  C_ORANGE),
        components.kpi_card('Interação Humana',   f"{pct:.1f}%",                    'fas fa-user',   C_RED),
        components.kpi_card('Pendência Humana',   f"{humanas:,}".replace(',', '.'),  'fas fa-user',   C_RED),
        components.kpi_card('Pendência Sistema',  f"{sistemas:,}".replace(',', '.'), 'fas fa-robot',  C_PURPLE),
    ])

    charts_row1 = _grid(
        _chart_card('Volume em Aberto por Tipo de Pendência', _graph(fig_volume)),
        _chart_card('Evolução Temporal',                      _graph(fig_temporal)),
        _chart_card('Composição de Pendências',               _graph(fig_pie)),
        cols=3,
    )

    charts_row2 = _grid(
        _chart_card(
            'Top 10 Tarefas em Aberto',
            _graph(charting.create_table_chart(
                tarefas, 'Tarefa', 'nomeTarefa', 'totalCount', 'totalCount',
            ), height=280),
        ),
        _chart_card(
            'Top 10 Usuários com Notas',
            _graph(charting.create_table_chart(
                usuarios, 'Usuário', 'userName', 'totalCount', 'totalCount',
            ), height=280),
        ),
        cols=2,
    )

    analytic = charting.create_analytic_table(
        id='tabela-analitica-notas-aberto', data=[], columns=[],
    )

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'},
        children=[
            _section('Indicadores de Notas em Aberto', kpi_cards),
            charts_row1,
            charts_row2,
            analytic,
        ],
    )


# ── Visão Geral ───────────────────────────────────────────────────────────────

def get_resumo_layout(captura_data, divergencia_data, notas_data, selected_grain='ME'):
    """
    Compiled overview: top KPIs + one chart from each operational area.
    The goal is to give a full story of the customer's operation at a glance:
      1. How many notes came in and how automated the ingestion is
      2. What portion has divergences that need attention
      3. How many are still open waiting for resolution
    """
    # ── Extract series ────────────────────────────────────────────────────────
    cap_series  = (captura_data     or {}).get('series', [])
    div_series  = (divergencia_data or {}).get('series', [])
    ab_series   = (notas_data       or {}).get('series', [])

    # ── Aggregate KPIs ────────────────────────────────────────────────────────
    total_cap   = sum(d.get('totalCount',          0) for d in cap_series)
    total_auto  = sum(d.get('totalAuto',           0) for d in cap_series)
    total_div   = sum(d.get('totalComDivergencia', 0) for d in div_series)
    total_notas = sum(d.get('totalCount',          0) for d in div_series) or 1
    total_ab    = sum(d.get('totalEmAberto',       0) for d in ab_series)
    total_hum   = sum(d.get('totalEmAbertoHumanas',0) for d in ab_series)

    auto_pct  = (total_auto / total_cap  * 100) if total_cap  > 0 else 0
    div_pct   = (total_div  / total_notas * 100) if total_notas > 0 else 0
    hum_pct   = (total_hum  / total_ab   * 100) if total_ab   > 0 else 0

    # ── KPI row ───────────────────────────────────────────────────────────────
    kpi_cards = _kpi_row([
        components.kpi_card(
            'Total Ingressado',
            f"{total_cap:,}".replace(',', '.'),
            'fas fa-file-invoice', C_PURPLE,
        ),
        components.kpi_card(
            'Ingresso Automático',
            f"{auto_pct:.1f}%",
            'fas fa-bolt', C_ORANGE,
        ),
        components.kpi_card(
            'Com Divergência',
            f"{div_pct:.1f}%",
            'fas fa-exclamation-triangle', C_RED,
        ),
        components.kpi_card(
            'Em Aberto',
            f"{total_ab:,}".replace(',', '.'),
            'fas fa-clock', C_ORANGE,
        ),
        components.kpi_card(
            'Aguardando Usuário',
            f"{hum_pct:.1f}%",
            'fas fa-user-clock', C_RED,
        ),
    ])

    # ── Story 1 – Ingresso ────────────────────────────────────────────────────
    cap_chart_data = aggregate_by_grain(
        cap_series, sum_cols=['totalCount', 'totalAuto'], grain=selected_grain,
    )
    for r in cap_chart_data:
        r['manualCount'] = r['totalCount'] - r['totalAuto']
        r['autoPct']     = (r['totalAuto'] / r['totalCount'] * 100) if r['totalCount'] > 0 else 0

    fig_ingresso = charting.create_combined_chart(
        cap_chart_data,
        bar_keys=['totalAuto', 'manualCount'],
        line_key='autoPct',
        bar_colors=[C_PURPLE, '#c4b5fd'],
        bar_names=['Automático', 'Manual'],
    )

    # ── Story 2 – Divergências ────────────────────────────────────────────────
    div_chart_data = aggregate_by_grain(
        div_series, sum_cols=['totalCount', 'totalComDivergencia'], grain=selected_grain,
    )
    for r in div_chart_data:
        r['semDivergencia'] = r['totalCount'] - r['totalComDivergencia']
        r['divPct']         = (r['totalComDivergencia'] / r['totalCount'] * 100) if r['totalCount'] > 0 else 0

    fig_divergencia = charting.create_combined_chart(
        div_chart_data,
        bar_keys=['totalComDivergencia', 'semDivergencia'],
        line_key='divPct',
        bar_colors=[C_RED, '#fca5a5'],
        bar_names=['Com Divergência', 'Sem Divergência'],
    )

    # ── Story 3 – Notas em Aberto ─────────────────────────────────────────────
    ab_chart_data = aggregate_by_grain(
        ab_series, sum_cols=['totalEmAberto', 'totalEmAbertoHumanas'], grain=selected_grain,
    )
    for r in ab_chart_data:
        r['totalSistema'] = r['totalEmAberto'] - r['totalEmAbertoHumanas']

    fig_aberto = charting.create_combined_chart(
        ab_chart_data,
        bar_keys=['totalEmAbertoHumanas', 'totalSistema'],
        bar_colors=[C_RED, C_ORANGE],
        bar_names=['Pendência Humana', 'Pendência Sistema'],
    )
    fig_aberto.update_layout(barmode='stack')

    # ── Assemble ──────────────────────────────────────────────────────────────
    charts_row = _grid(
        _chart_card('Notas por Tipo de Ingresso',    _graph(fig_ingresso)),
        _chart_card('Divergências ao Longo do Tempo', _graph(fig_divergencia)),
        _chart_card('Notas em Aberto por Pendência',  _graph(fig_aberto)),
        cols=3,
    )

    # Supplier and divergence type tables side-by-side
    suppliers  = (captura_data     or {}).get('suppliers', [])
    tipos_div  = (divergencia_data or {}).get('types',    [])
    usuarios   = (notas_data       or {}).get('usuarios', [])

    tables_row = _grid(
        _chart_card(
            'Top Fornecedores por Volume',
            _graph(charting.create_table_chart(
                suppliers, 'Fornecedor', 'supplierCnpj', 'totalCount', 'totalAuto',
            ), height=260),
        ),
        _chart_card(
            'Principais Divergências',
            _graph(charting.create_table_chart(
                tipos_div, 'Tipo', 'nomeDivergencia', 'totalCount', 'totalCount',
            ), height=260),
        ),
        _chart_card(
            'Usuários com Notas em Aberto',
            _graph(charting.create_table_chart(
                usuarios, 'Usuário', 'userName', 'totalCount', 'totalCount',
            ), height=260),
        ),
        cols=3,
    )

    no_data_banner = None
    if not cap_series and not div_series and not ab_series:
        return _no_data()

    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'gap': '24px'},
        children=[
            _section('Principais Indicadores', kpi_cards),
            charts_row,
            tables_row,
        ],
    )
