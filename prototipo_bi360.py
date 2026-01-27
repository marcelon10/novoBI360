import dash
from dash import dcc, html, Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import math
import random
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import requests

API_URL = "http://localhost:8000/graphql"

def fetch_graphql_data(query_string):
    # (Same function you just tested)
    response = requests.post(API_URL, json={'query': query_string})
    return response.json()

# --- The entire HTML content for the "Resumo" tab ---
html_homepage_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Principal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://www.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        /* Custom styles to enhance the design */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #111827; /* bg-gray-900 */
        }
        /* Style for the SVG connector path to ensure it's dotted */
        .connector-path {
            stroke: #8B5CF6; /* Corresponds to Tailwind's purple-500 */
            stroke-width: 2;
            fill: none;
            stroke-dasharray: 5 5;
        }
    </style>
</head>
<body class="bg-gray-900 text-white p-4 sm:p-6 md:p-8">

    <div class="max-w-5xl mx-auto relative">
        <button id="open-alerts-btn" class="absolute top-0 right-0 bg-red-600 text-white font-bold py-2 px-4 rounded-lg shadow-lg hover:bg-red-700 transition-colors duration-300">
            Alertas da Operação
        </button>

        <main class="flex flex-col items-center pt-16">

            <div class="w-full flex flex-col md:flex-row items-start justify-center gap-6">
                <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                    <p class="text-lg text-purple-200 uppercase font-bold">Notas Ingressadas</p>
                    <p class="text-6xl font-black my-2">25.301</p>
                    <p class="text-md text-purple-300">Nos últimos 30 dias</p>
                </div>
                <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-4xl font-bold text-purple-400">23.456</p>
                    <p class="text-gray-300 mt-2 mb-4">Foram ingressadas <span class="font-semibold text-white">automaticamente</span> na ferramenta.</p>
                    <a href="/captura" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group">
                        Clique aqui para ir ao BI de Ingresso de Notas
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>

            <div class="w-full h-24 relative">
                <svg width="100%" height="100%" class="absolute left-0 top-0">
                    <path d="M 25% 0 C 25% 50%, 75% 50%, 75% 100%" class="connector-path"/>
                </svg>
            </div>

            <div class="w-full flex flex-col md:flex-row-reverse items-start justify-center gap-6">
                <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                    <p class="text-2xl font-bold leading-tight">Das 25.301 notas ingressadas, <span class="text-6xl font-black block">45%</span> apresentaram divergências</p>
                </div>
                <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-4xl font-bold text-orange-400">11.385</p>
                    <p class="text-gray-300 mt-2 mb-4">Notas apresentaram ao menos uma <span class="font-semibold text-white">divergência</span>.</p>
                    <a href="/divergencias" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group">
                        Clique aqui para ir ao BI de Divergências
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>

            <div class="w-full h-24 relative">
                <svg width="100%" height="100%" class="absolute left-0 top-0">
                    <path d="M 75% 0 C 75% 50%, 25% 50%, 25% 100%" class="connector-path"/>
                </svg>
            </div>

            <div class="w-full flex flex-col md:flex-row items-start justify-center gap-6">
                 <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                     <p class="text-2xl font-bold leading-tight">Das 25.301 notas, <span class="text-6xl font-black block">12.356</span> já foram escrituradas</p>
                </div>
                 <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-4xl font-bold text-yellow-400">12.945</p>
                    <p class="text-gray-300 mt-2 mb-4">Notas ainda estão <span class="font-semibold text-white">em aberto</span>, aguardando alguma ação.</p>
                    <a href="/notas-em-aberto" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group">
                        Clique aqui para ir ao BI de Notas em Aberto
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>
            
            <div class="w-full h-24 relative">
                <svg width="100%" height="100%" class="absolute left-0 top-0">
                    <path d="M 25% 0 C 25% 50%, 75% 50%, 75% 100%" class="connector-path"/>
                </svg>
            </div>

            <div class="w-full flex flex-col md:flex-row-reverse items-start justify-center gap-6">
                <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                    <p class="text-2xl font-bold leading-tight">Dessas 12.356 escrituradas, <span class="text-6xl font-black block">95%</span> foram concluídas com sucesso</p>
                </div>
                <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-2xl font-bold text-green-400">11.786 concluídas com sucesso</p>
                    <p class="text-lg text-red-400 mt-2">370 canceladas</p>
                    <p class="text-lg text-gray-400 mt-1">200 arquivadas</p>
                    <a href="/tarefas" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group mt-4">
                        Clique aqui para ir ao dashboard de finalização
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>

            <div class="w-full h-24 relative">
                <svg width="100%" height="100%" class="absolute left-0 top-0">
                    <path d="M 75% 0 C 75% 50%, 25% 50%, 25% 100%" class="connector-path"/>
                </svg>
            </div>

            <div class="w-full flex flex-col md:flex-row items-start justify-center gap-6">
                <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                    <p class="text-2xl font-bold leading-tight">Das 12.356 notas escrituradas, <span class="text-6xl font-black block">46%</span> percorreram o fluxo 100% automatizado</p>
                </div>
                <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-4xl font-bold text-cyan-400">5.682</p>
                    <p class="text-gray-300 mt-2 mb-4">Notas percorreram todo o fluxo <span class="font-semibold text-white">sem intervenção manual</span>.</p>
                    <a href="/outros-motivos" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group">
                        Clique aqui para ir ao BI de Automação
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>

            <div class="w-full h-24 relative">
                <svg width="100%" height="100%" class="absolute left-0 top-0">
                    <path d="M 25% 0 C 25% 50%, 75% 50%, 75% 100%" class="connector-path"/>
                </svg>
            </div>

            <div class="w-full flex flex-col md:flex-row-reverse items-start justify-center gap-6">
                <div class="w-full md:w-1/2 bg-purple-600 shadow-2xl rounded-xl p-10 flex flex-col justify-center text-center transform hover:scale-105 transition-transform duration-300">
                    <p class="text-lg text-purple-200 uppercase font-bold">Tempo Médio de Escrituração</p>
                    <p class="text-6xl font-black my-2">7.42</p>
                    <p class="text-md text-purple-300">Dias úteis</p>
                </div>
                <div class="w-full md:w-1/2 bg-gray-800 border border-gray-700 rounded-xl p-10 flex flex-col justify-center md:mt-6">
                    <p class="text-2xl font-bold text-orange-400">10.43 dias <span class="text-lg text-gray-300 font-normal">com divergência</span></p>
                    <p class="text-2xl font-bold text-green-400 mt-2">5.32 dias <span class="text-lg text-gray-300 font-normal">sem divergência</span></p>
                    <a href="/leadtime" target="_top" class="text-purple-400 font-semibold hover:text-purple-300 transition-colors duration-300 group mt-4">
                        Clique aqui para ir ao dashboard de leadtime
                        <span class="inline-block transform group-hover:translate-x-1 transition-transform duration-300">&rarr;</span>
                    </a>
                </div>
            </div>

        </main>
    </div>

    <div id="alerts-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
        <div class="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-bold text-white">Alertas Importantes</h3>
                <button id="close-alerts-btn" class="text-gray-400 hover:text-white text-3xl">&times;</button>
            </div>
            <ul class="list-disc list-inside space-y-2 text-gray-300">
                <li>Alerta Ponto 1: Descrição do primeiro alerta importante.</li>
                <li>Alerta Ponto 2: Descrição do segundo alerta.</li>
                <li>Alerta Ponto 3: Terceiro item de alerta para a operação.</li>
                <li>Alerta Ponto 4: Quarto e último ponto de alerta.</li>
            </ul>
        </div>
    </div>

    <script>
        const openBtn = document.getElementById('open-alerts-btn');
        const closeBtn = document.getElementById('close-alerts-btn');
        const modal = document.getElementById('alerts-modal');

        if (openBtn && modal) {
            openBtn.addEventListener('click', () => {
                modal.classList.remove('hidden');
            });
        }

        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        }

        // Optional: Close when clicking outside the modal content
        if (modal) {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        }
    </script>

</body>
</html>
"""

# --- Initialize the Dash app with external stylesheet for icons ---
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
        dbc.themes.BOOTSTRAP
    ]
)
app.title = "BI360"

def get_ingresso_mensal():
    query = """
    query {
        getIngressoMensal {
            month
            totalCount
            autoPct
        }
    }
    """
    result = fetch_graphql_data(query)
    if 'data' in result and result['data']['getIngressoMensal']:
        # Return as a list of dicts, matching your original structure
        return result['data']['getIngressoMensal']
    return [] # Fallback

def get_ingresso_total():
    query = """
    query {
        getIngressoTotal {
            totalCount
            autoCount
        }
    }
    """
    result = fetch_graphql_data(query)
    if 'data' in result and result['data']['getIngressoTotal']:
        # Return as a list of dicts, matching your original structure
        return result['data']['getIngressoTotal']
    return [] # Fallback

# --- DUMMY DATA ---
monthly_data = [
    {'Month': 'Jan', 'Sucesso / Pago': 800, 'Arquivadas': 400, 'Em Aberto': 200, 'Canceladas': 100},
    {'Month': 'Fev', 'Sucesso / Pago': 950, 'Arquivadas': 450, 'Em Aberto': 250, 'Canceladas': 120},
    {'Month': 'Mar', 'Sucesso / Pago': 1000, 'Arquivadas': 500, 'Em Aberto': 150, 'Canceladas': 80},
    {'Month': 'Abr', 'Sucesso / Pago': 1100, 'Arquivadas': 520, 'Em Aberto': 180, 'Canceladas': 90},
    {'Month': 'Mai', 'Sucesso / Pago': 1050, 'Arquivadas': 480, 'Em Aberto': 220, 'Canceladas': 110},
    {'Month': 'Jun', 'Sucesso / Pago': 1200, 'Arquivadas': 550, 'Em Aberto': 200, 'Canceladas': 100},
    {'Month': 'Jul', 'Sucesso / Pago': 1250, 'Arquivadas': 580, 'Em Aberto': 210, 'Canceladas': 105},
    {'Month': 'Ago', 'Sucesso / Pago': 1300, 'Arquivadas': 600, 'Em Aberto': 230, 'Canceladas': 115},
    {'Month': 'Set', 'Sucesso / Pago': 1150, 'Arquivadas': 540, 'Em Aberto': 190, 'Canceladas': 95},
    {'Month': 'Out', 'Sucesso / Pago': 1400, 'Arquivadas': 650, 'Em Aberto': 250, 'Canceladas': 125},
    {'Month': 'Nov', 'Sucesso / Pago': 1500, 'Arquivadas': 700, 'Em Aberto': 280, 'Canceladas': 140},
    {'Month': 'Dez', 'Sucesso / Pago': 1600, 'Arquivadas': 750, 'Em Aberto': 300, 'Canceladas': 150},
]

# --- DATA PROCESSING ---
all_columns = list(monthly_data[0].keys())
unique_cols = set(all_columns)
for month in monthly_data:
    month['posted'] = month['Sucesso / Pago'] + month['Arquivadas']
    month['not_posted'] = month['Em Aberto'] + month['Canceladas']
    month['total'] = month['posted'] + month['not_posted']
    month['automatic'] = math.floor(month['total'] * 0.85)
    month['manual'] = month['total'] - month['automatic']
    month['auto_pct'] = month['automatic'] / month['total'] * 100 if month['total'] > 0 else 0
    unique_cols.update(['posted', 'not_posted', 'total', 'automatic', 'manual', 'auto_pct'])
all_columns = sorted(list(unique_cols))


totals = {
    'successful_paid': sum(d['Sucesso / Pago'] for d in monthly_data),
    'archived': sum(d['Arquivadas'] for d in monthly_data),
    'open_invoices': sum(d['Em Aberto'] for d in monthly_data),
    'canceled_invoices': sum(d['Canceladas'] for d in monthly_data),
}
totals['posted_invoices'] = totals['successful_paid'] + totals['archived']
totals['not_posted'] = totals['open_invoices'] + totals['canceled_invoices']
totals['total_invoices'] = totals['posted_invoices'] + totals['not_posted']
totals['automatic_invoices'] = sum(d['automatic'] for d in monthly_data)

# --- Helper functions for dummy data generation ---
def get_fornecedores_data():
    random.seed(10)
    data = []
    for i in range(20):
        total_notas = random.randint(50, 1500)
        manual_notas = random.randint(0, int(total_notas * 0.4))
        percentual_manual = (manual_notas / total_notas * 100) if total_notas > 0 else 0
        data.append({
            "Razão Social Fornecedor": f"Fornecedor Exemplo {i+1} LTDA",
            "Total de Notas": total_notas,
            "Percentual de Ingresso Manual": f"{percentual_manual:.1f}%"
        })
    return sorted(data, key=lambda x: x['Total de Notas'], reverse=True)

def get_prefeituras_data():
    random.seed(20)
    data = []
    for i in range(20):
        total_notas = random.randint(20, 800)
        manual_notas = random.randint(0, int(total_notas * 0.3))
        percentual_manual = (manual_notas / total_notas * 100) if total_notas > 0 else 0
        data.append({
            "Prefeitura": f"Prefeitura de {chr(65+i)} Cidade",
            "Total de Notas": total_notas,
            "Percentual de Ingresso Manual": f"{percentual_manual:.1f}%"
        })
    return sorted(data, key=lambda x: x['Total de Notas'], reverse=True)

# --- New Dummy Data for the Analytic Table (Captura Tab) ---
def get_detailed_invoice_data():
    random.seed(42)
    data = []
    for i in range(100):
        emission_date = datetime.now() - timedelta(days=random.randint(1, 365))
        ingress_date = emission_date + timedelta(hours=random.randint(1, 48))
        data.append({
            "ID V360": 12345 + i,
            "Data de Emissão": emission_date.strftime('%d/%m/%Y'),
            "Data de Ingresso": ingress_date.strftime('%d/%m/%Y'),
            "Razão Social Fornecedor": f"Fornecedor Exemplo {random.randint(1, 20)} LTDA",
            "Razão Social Tomador": f"Tomador Exemplo {random.randint(1, 5)} SA",
            "Tipo de Documento": random.choice(['NFS-e', 'CT-e', 'NF-e']),
            "Tipo de Ingresso": random.choice(['Automático', 'Manual', 'Email']),
            "Valor Total": round(random.uniform(100.0, 5000.0), 2)
        })
    return data

detailed_invoice_data = get_detailed_invoice_data()
analytic_table_columns = [
    'ID V360', 'Data de Emissão', 'Data de Ingresso', 'Razão Social Fornecedor',
    'Razão Social Tomador', 'Tipo de Documento', 'Tipo de Ingresso', 'Valor Total'
]

# --- DUMMY DATA FOR AUTOMATISMO TAB ---
def get_monthly_automation_data():
    data = []
    sem_intervencao_base = 400
    com_intervencao_base = 500
    for month in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        sem_intervencao = sem_intervencao_base + random.randint(-50, 100)
        com_intervencao = com_intervencao_base + random.randint(-70, 50)
        total = sem_intervencao + com_intervencao
        auto_pct = (sem_intervencao / total * 100) if total > 0 else 0
        data.append({
            "Month": month,
            "Sem Intervenção Manual": sem_intervencao,
            "Com Intervenção Manual": com_intervencao,
            "auto_pct": auto_pct
        })
        sem_intervencao_base += 20
        com_intervencao_base -= 10
    return data

monthly_automation_data = get_monthly_automation_data()
manual_task_names = ["Aprovação de Pagamento", "Correção de Divergência", "Análise Fiscal", "Validação de Centro de Custo", "Alocação de Pedido"]

# NEW DATA FOR AUTOMATISMO STACKED BAR CHART
automation_stacked_data = {
    'Tipo de Documento': [
        {'Category': 'NFS-e', 'Sem Intervenção Manual': 850, 'Com Intervenção Manual': 150},
        {'Category': 'CT-e',  'Sem Intervenção Manual': 600, 'Com Intervenção Manual': 400},
        {'Category': 'NF-e',  'Sem Intervenção Manual': 700, 'Com Intervenção Manual': 200},
        {'Category': 'Fatura','Sem Intervenção Manual': 300, 'Com Intervenção Manual': 350},
    ],
    'Unidade de Negócio': [
        {'Category': 'Unidade SP', 'Sem Intervenção Manual': 1200, 'Com Intervenção Manual': 300},
        {'Category': 'Unidade RJ', 'Sem Intervenção Manual': 950, 'Com Intervenção Manual': 250},
        {'Category': 'Unidade MG', 'Sem Intervenção Manual': 400, 'Com Intervenção Manual': 500},
    ],
    'Nome do Fluxo': [
        {'Category': 'Fluxo Padrão', 'Sem Intervenção Manual': 2000, 'Com Intervenção Manual': 200},
        {'Category': 'Fluxo Exceção', 'Sem Intervenção Manual': 100, 'Com Intervenção Manual': 600},
        {'Category': 'Fluxo Simplificado', 'Sem Intervenção Manual': 450, 'Com Intervenção Manual': 50},
    ]
}

# NEW DATA FOR CAPTURA STACKED BAR CHART
captura_stacked_data = {
    'Tipo de Documento': [
        {'Category': 'Serviço', 'Captura Automática': 8500, 'Email': 2000, 'Inserção Manual': 650},
        {'Category': 'Material', 'Captura Automática': 6000, 'Email': 1500, 'Inserção Manual': 400},
        {'Category': 'Transporte', 'Captura Automática': 4000, 'Email': 800, 'Inserção Manual': 250},
        {'Category': 'Concessionárias', 'Captura Automática': 1200, 'Email': 250, 'Inserção Manual': 60},
    ],
    'Unidade de Negócio': [
        {'Category': 'Unidade SP', 'Captura Automática': 10000, 'Email': 2500, 'Inserção Manual': 800},
        {'Category': 'Unidade RJ', 'Captura Automática': 7500, 'Email': 1800, 'Inserção Manual': 450},
        {'Category': 'Unidade MG', 'Captura Automática': 2200, 'Email': 250, 'Inserção Manual': 110},
    ]
}

def get_top_manual_tasks_data():
    data = []
    for task in manual_task_names:
        data.append({
            "Tarefa": task,
            "Ocorrências": random.randint(100, 2000),
            "Tempo Médio (horas)": f"{random.uniform(1, 24):.1f}h"
        })
    return sorted(data, key=lambda x: x['Ocorrências'], reverse=True)

def get_top_analysts_data():
    analysts = ["Ana Silva", "Bruno Costa", "Carla Dias", "Daniel Souza", "Eduarda Lima"]
    data = []
    for analyst in analysts:
        data.append({
            "Analista": analyst,
            "Tarefas Concluídas": random.randint(50, 500),
            "Tempo Médio (min)": f"{random.uniform(5, 60):.1f}m"
        })
    return sorted(data, key=lambda x: x['Tarefas Concluídas'], reverse=True)
    
def get_detailed_task_data():
    data = []
    for i in range(200):
        creation_date_note = datetime.now() - timedelta(days=random.randint(10, 365))
        creation_date_task = creation_date_note + timedelta(hours=random.randint(1, 48))
        finalization_date_task = creation_date_task + timedelta(minutes=random.randint(5, 5*24*60))
        time_delta = finalization_date_task - creation_date_task
        days, seconds = time_delta.days, time_delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60

        data.append({
            "ID Tarefa V360": 90000 + i,
            "ID Nota V360": 12000 + i,
            "Data de Criação da Tarefa": creation_date_task.strftime('%d/%m/%Y %H:%M'),
            "Data de Finalização da Tarefa": finalization_date_task.strftime('%d/%m/%Y %H:%M'),
            "Data de Criação da Nota": creation_date_note.strftime('%d/%m/%Y'),
            "Razão Social Fornecedor": f"Fornecedor Exemplo {random.randint(1, 20)} LTDA",
            "Razão Social Tomador": f"Tomador Exemplo {random.randint(1, 5)} SA",
            "Nome da Tarefa": random.choice(manual_task_names),
            "Tipo do Documento": random.choice(['NFS-e', 'CT-e', 'NF-e']),
            "Tipo da Tarefa": random.choice(['Automática', 'Manual']),
            "Tempo de Finalização da Tarefa": f"{hours}h {minutes}m",
            "Finalizada por": random.choice(["Ana Silva", "Bruno Costa", "Carla Dias", "Daniel Souza", "Sistema"])
        })
    return data

detailed_task_data = get_detailed_task_data()
task_analytic_columns = list(detailed_task_data[0].keys())


# --- DUMMY DATA FOR DIVERGENCIAS TAB ---
def get_monthly_divergence_data():
    data = []
    for month in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        total_notes = random.randint(1500, 2500)
        divergent_notes = int(total_notes * random.uniform(0.3, 0.55))
        pct_divergence = (divergent_notes / total_notes * 100) if total_notes > 0 else 0
        data.append({
            'Month': month,
            'Notas com Divergência': divergent_notes,
            'pct_divergence': pct_divergence
        })
    return data

divergence_type_data = {
    'Tipo de Divergência': [
        {'Category': 'Valor Divergente', 'Ocorrências': 4200},
        {'Category': 'Pedido Inválido', 'Ocorrências': 2800},
        {'Category': 'CNPJ Incorreto', 'Ocorrências': 1500},
        {'Category': 'Item não Cadastrado', 'Ocorrências': 1100},
        {'Category': 'Alíquota de Imposto', 'Ocorrências': 850},
        {'Category': 'Outros', 'Ocorrências': 935}
    ]
}

def get_top_divergence_suppliers_data():
    data = []
    for i in range(1, 11):
        data.append({
            "Fornecedor": f"Fornecedor Divergente {i}",
            "Notas com Divergência": random.randint(50, 400),
            "Valor Total (R$)": f"R$ {random.uniform(10000, 150000):,.2f}"
        })
    return sorted(data, key=lambda x: x['Notas com Divergência'], reverse=True)

def get_detailed_divergence_data():
    divergence_types = [d['Category'] for d in divergence_type_data['Tipo de Divergência']]
    data = []
    for i in range(150):
        data.append({
            "ID Nota V360": 50000 + i,
            "Fornecedor": f"Fornecedor Divergente {random.randint(1, 10)}",
            "Data da Divergência": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%d/%m/%Y'),
            "Tipo de Divergência": random.choice(divergence_types),
            "Valor da Nota (R$)": round(random.uniform(500, 8000), 2),
            "Status": random.choice(["Em Análise", "Corrigida", "Aguardando Fornecedor"]),
            "Analista Responsável": random.choice(["Ana Silva", "Bruno Costa", "Carla Dias"])
        })
    return data

detailed_divergence_data = get_detailed_divergence_data()
divergence_analytic_columns = list(detailed_divergence_data[0].keys())

# --- DUMMY DATA FOR NOTAS EM ABERTO TAB ---
open_notes_aging_data = [
    {'Faixa de Atraso': '0-7 dias', 'Quantidade': 3450},
    {'Faixa de Atraso': '8-15 dias', 'Quantidade': 2800},
    {'Faixa de Atraso': '16-30 dias', 'Quantidade': 1980},
    {'Faixa de Atraso': '31-60 dias', 'Quantidade': 1200},
    {'Faixa de Atraso': '60+ dias', 'Quantidade': 560}
]

open_notes_by_status_data = {
    'Unidade de Negócio': [
        {'Category': 'Unidade SP', 'Aprovação Pendente': 1500, 'Análise Fiscal': 800, 'Aguardando Pedido': 400},
        {'Category': 'Unidade RJ', 'Aprovação Pendente': 1200, 'Análise Fiscal': 650, 'Aguardando Pedido': 350},
        {'Category': 'Unidade MG', 'Aprovação Pendente': 800, 'Análise Fiscal': 400, 'Aguardando Pedido': 700},
    ]
}

def get_top_pending_suppliers_data():
    data = []
    for i in range(1, 11):
        data.append({
            "Fornecedor": f"Fornecedor Pendente {i}",
            "Notas em Aberto": random.randint(30, 250),
            "Valor em Aberto (R$)": f"R$ {random.uniform(20000, 250000):,.2f}"
        })
    return sorted(data, key=lambda x: x['Notas em Aberto'], reverse=True)

def get_detailed_open_notes_data():
    statuses = ['Aprovação Pendente', 'Análise Fiscal', 'Aguardando Pedido']
    data = []
    for i in range(150):
        creation_date = datetime.now() - timedelta(days=random.randint(1, 70))
        age = (datetime.now() - creation_date).days
        data.append({
            "ID Nota V360": 60000 + i,
            "Fornecedor": f"Fornecedor Pendente {random.randint(1, 10)}",
            "Data de Criação": creation_date.strftime('%d/%m/%Y'),
            "Idade (dias)": age,
            "Etapa Atual": random.choice(statuses),
            "Valor (R$)": round(random.uniform(500, 10000), 2),
            "Usuário Responsável": random.choice(["Daniel Souza", "Eduarda Lima", "Sistema"])
        })
    return data

detailed_open_notes_data = get_detailed_open_notes_data()
open_notes_analytic_columns = list(detailed_open_notes_data[0].keys())

# --- DUMMY DATA FOR LEADTIME TAB ---
def get_monthly_leadtime_data():
    data = []
    base_leadtime = 10
    for month in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        avg_leadtime = base_leadtime + random.uniform(-1.5, 1.5)
        data.append({
            "Month": month,
            "Leadtime Médio (dias)": round(avg_leadtime, 2),
            "Leadtime com Divergência (dias)": round(avg_leadtime * 1.4, 2),
            "Leadtime sem Divergência (dias)": round(avg_leadtime * 0.7, 2),
        })
        base_leadtime -= 0.2
    return data
    
leadtime_by_step_data = [
    {'Etapa': 'Ingresso -> Análise Fiscal', 'Tempo Médio (dias)': 1.2},
    {'Etapa': 'Análise Fiscal -> Aprovação', 'Tempo Médio (dias)': 3.5},
    {'Etapa': 'Aprovação -> Escrituração', 'Tempo Médio (dias)': 2.1},
    {'Etapa': 'Escrituração -> Pagamento', 'Tempo Médio (dias)': 0.8},
]

def get_detailed_leadtime_data():
    data = []
    for i in range(150):
        total_leadtime = random.uniform(3, 15)
        data.append({
            "ID Nota V360": 70000 + i,
            "Fornecedor": f"Fornecedor Exemplo {random.randint(1, 20)} LTDA",
            "Data de Conclusão": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%d/%m/%Y'),
            "Leadtime Total (dias)": round(total_leadtime, 1),
            "Teve Divergência?": random.choice(["Sim", "Não"]),
            "Tipo de Documento": random.choice(['NFS-e', 'CT-e', 'NF-e']),
            "Fluxo 100% Automático?": random.choice(["Sim", "Não"]),
        })
    return data

detailed_leadtime_data = get_detailed_leadtime_data()
leadtime_analytic_columns = list(detailed_leadtime_data[0].keys())


# --- CHARTING FUNCTIONS ---

def create_stacked_bar_chart(data, x_key, y_keys, colors, title):
    fig = go.Figure()
    x_values = [d[x_key] for d in data]

    for y_key, color in zip(y_keys, colors):
        values = [d[y_key] for d in data]
        name = y_key.replace('_', ' ').title()
        fig.add_trace(go.Bar(
            x=x_values, y=values, name=name, marker_color=color,
            text=values, texttemplate='%{text:,.0f}',
            textposition='inside', insidetextanchor='middle'
        ))

    fig.update_layout(
        barmode='stack', title_text=title, title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(color='#d1d5db')),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def create_simple_bar_chart(data, x_key, y_key, color, title, orientation='v'):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x_key] if orientation == 'v' else data[y_key],
        y=data[y_key] if orientation == 'v' else data[x_key],
        marker_color=color,
        orientation=orientation
    ))
    fig.update_layout(
        title_text=title, title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def create_pie_chart(labels, values, colors, title, hole=.3):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=hole, marker_colors=colors)])
    fig.update_traces(textinfo='percent+label', pull=[0.05] * len(labels))
    fig.update_layout(
        title_text=title, title_x=0.5, showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db")
    )
    return fig

def create_bar_line_chart(data, bar_keys, line_key, bar_colors, line_color, title, bar_names=None, line_name=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    months = [d['month'] for d in data]

    bar_names = bar_names or [k.replace('_', ' ').title() for k in bar_keys]
    line_name = line_name or line_key.replace('_', ' ').title()
    
    for key, name, color in zip(bar_keys, bar_names, bar_colors):
        bar_values = [d[key] for d in data]
        fig.add_trace(go.Bar(x=months, y=bar_values, name=name, marker_color=color), secondary_y=False)

    fig.add_trace(go.Scatter(x=months, y=[d[line_key] for d in data], name=line_name, mode='lines+markers', line=dict(color=line_color)), secondary_y=True)
    
    fig.update_layout(
        barmode='stack', title_text=title, title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#d1d5db')),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db")
    )
    fig.update_yaxes(title_text="Quantidade de Notas", secondary_y=False, color='#d1d5db', showgrid=False)
    fig.update_yaxes(title_text="Percentual (%)", secondary_y=True, color='#d1d5db', showgrid=False, range=[0, 100])
    fig.update_xaxes(color='#d1d5db', showgrid=False)
    return fig

def create_multi_line_chart(data, x_key, y_keys, colors, title, y_title):
    fig = go.Figure()
    for y_key, color in zip(y_keys, colors):
        fig.add_trace(go.Scatter(
            x=[d[x_key] for d in data],
            y=[d[y_key] for d in data],
            name=y_key.replace('_', ' ').title(),
            mode='lines+markers',
            line=dict(color=color)
        ))
    fig.update_layout(
        title_text=title, title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#d1d5db')),
        font=dict(family="Inter, sans-serif", size=12, color="#d1d5db")
    )
    fig.update_yaxes(title_text=y_title, color='#d1d5db', showgrid=False)
    fig.update_xaxes(color='#d1d5db', showgrid=False)
    return fig

def create_table(data, title, visible_columns=None):
    if not data: return go.Figure()
    
    headers = visible_columns or list(data[0].keys())
    
    cells_data = []
    for col in headers:
        formatted_col = []
        for row in data:
            val = row.get(col)
            if isinstance(val, (int, float)) and 'ID' not in col and 'Data' not in col:
                 formatted_col.append(f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                 formatted_col.append(val)
        cells_data.append(formatted_col)

    fig = go.Figure(data=[go.Table(
        header=dict(values=headers, fill_color='#592a9e', align='left', font=dict(color='white')),
        cells=dict(values=cells_data, fill_color='#1f2937', align='left', font=dict(color='#d1d5db')))
    ])
    fig.update_layout(
        title_text=title, title_x=0.5,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#d1d5db")
    )
    return fig

def create_styled_list_table(title, data, primary_col, metric_cols, table_id):
    header_cols = [primary_col] + metric_cols
    flex_shares = ['2', '1', '1']
    header = html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px 5px', 'borderBottom': '1px solid #4b5563'}, children=[
        html.Button(col, id={'type': 'sort-btn', 'table_id': table_id, 'col': col}, n_clicks=0, style={'background': 'none', 'border': 'none', 'color': '#9ca3af', 'fontWeight': 'bold', 'padding': '0', 'margin': '0', 'cursor': 'pointer', 'flex': flex, 'textAlign': 'right' if i > 0 else 'left'}) 
        for i, (col, flex) in enumerate(zip(header_cols, flex_shares))
    ])

    rows = [
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '12px 5px', 'borderBottom': '1px solid #374151'}, children=[
            html.P(item[primary_col], style={'flex': '2', 'margin': '0', 'fontSize': '0.9em'}),
            html.P(f"{item[metric_cols[0]]:,}".replace(",", "."), style={'flex': '1', 'textAlign': 'right', 'margin': '0', 'fontWeight': 'bold'}),
            html.P(str(item[metric_cols[1]]), style={'flex': '1', 'textAlign': 'right', 'margin': '0', 'color': '#f59e0b'})
        ]) for item in data
    ]
    
    return html.Div([
        html.H4(title, style={'textAlign': 'center', 'marginBottom': '15px'}),
        header,
        html.Div(rows, id={'type': 'list-table-body', 'table_id': table_id}, style={'maxHeight': '400px', 'overflowY': 'auto'})
    ])

# --- Reusable KPI/Filter Components ---
def create_captura_kpi_layout(data):
    
    total_invoices = data.get('totalCount', 0)
    automatic_invoices = data.get('autoCount', 0)
    manual_invoices = total_invoices - automatic_invoices
    auto_pct = (automatic_invoices / total_invoices * 100) if total_invoices > 0 else 0

    return html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center', 'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-around'}, children=[
        html.Div([
            html.H2(f"{total_invoices:,}".replace(",", "."), style={'margin': '0', 'color': '#8B5CF6', 'fontSize': '3em', 'fontWeight': '900'}),
            html.P("Notas Ingressadas no Período", style={'margin': '0', 'color': '#9ca3af', 'fontSize': '1em'})]),
        html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'margin': '20px 0'}, children=[
            html.Div([html.P(f"{automatic_invoices:,}".replace(",", "."), style={'fontSize': '2em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Capturadas Automaticamente", style={'color': '#9ca3af', 'margin': '0'})]),
            html.Div([html.P(f"{manual_invoices:,}".replace(",", "."), style={'fontSize': '2em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Ingressadas Manualmente", style={'color': '#9ca3af', 'margin': '0'})])]),
        html.Div([
            html.H3(f"{auto_pct:.0f}%", style={'margin': '0', 'color': '#00b894', 'fontSize': '2.5em', 'fontWeight': 'bold'}),
            html.P("de automatismo no ingresso de notas", style={'margin': '0', 'color': '#9ca3af'})])])

def create_automatismo_kpi_layout():
    return html.Div(
        style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center', 'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'gap': '20px'},
        children=[
            html.Div([
                html.H2("5.682", style={'margin': '0', 'color': '#2dd4bf', 'fontSize': '4em', 'fontWeight': '900'}),
                html.P("notas foram escrituradas sem nenhuma ação manual", style={'margin': '0', 'color': '#9ca3af', 'fontSize': '1em'})
            ]),
            html.Div([
                html.H3("46%", style={'margin': '0', 'color': '#a78bfa', 'fontSize': '2.5em', 'fontWeight': 'bold'}),
                html.P("das 12.356 notas escrituradas no período", style={'margin': '0', 'color': '#9ca3af'})
            ])
        ]
    )

def create_divergencias_kpi_layout():
    return html.Div(
        style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center', 'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'gap': '20px'},
        children=[
            html.Div([
                html.H2("11.385", style={'margin': '0', 'color': '#fb923c', 'fontSize': '4em', 'fontWeight': '900'}),
                html.P("Notas apresentaram divergências", style={'margin': '0', 'color': '#9ca3af', 'fontSize': '1em'})
            ]),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'margin': '20px 0'}, children=[
                html.Div([html.H3("45%", style={'fontSize': '2.5em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Do total de notas", style={'color': '#9ca3af', 'margin': '0'})]),
                html.Div([html.P("R$ 1.234.567,89", style={'fontSize': '1.8em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Valor total divergente", style={'color': '#9ca3af', 'margin': '0'})])]),
        ]
    )

def create_notas_aberto_kpi_layout():
    return html.Div(
        style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center', 'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'gap': '20px'},
        children=[
            html.Div([
                html.H2("12.945", style={'margin': '0', 'color': '#facc15', 'fontSize': '4em', 'fontWeight': '900'}),
                html.P("Notas em aberto", style={'margin': '0', 'color': '#9ca3af', 'fontSize': '1em'})
            ]),
             html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'margin': '20px 0'}, children=[
                html.Div([html.H3("18.5 dias", style={'fontSize': '2.2em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Idade média", style={'color': '#9ca3af', 'margin': '0'})]),
                html.Div([html.P("R$ 2.345.678,90", style={'fontSize': '1.8em', 'fontWeight': 'bold', 'color': '#d1d5db', 'margin': '0'}), html.P("Valor total em aberto", style={'color': '#9ca3af', 'margin': '0'})])]),
        ]
    )

def create_leadtime_kpi_layout():
    return html.Div(
        style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'textAlign': 'center', 'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'gap': '20px'},
        children=[
            html.Div([
                html.H2("7.42", style={'margin': '0', 'color': '#60a5fa', 'fontSize': '4em', 'fontWeight': '900'}),
                html.P("Dias úteis - Leadtime médio geral", style={'margin': '0', 'color': '#9ca3af', 'fontSize': '1em'})
            ]),
             html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'margin': '20px 0'}, children=[
                html.Div([html.P("10.43 dias", style={'fontSize': '2em', 'fontWeight': 'bold', 'color': '#fb923c', 'margin': '0'}), html.P("Com divergência", style={'color': '#9ca3af', 'margin': '0'})]),
                html.Div([html.P("5.32 dias", style={'fontSize': '2em', 'fontWeight': 'bold', 'color': '#2dd4bf', 'margin': '0'}), html.P("Sem divergência", style={'color': '#9ca3af', 'margin': '0'})])]),
        ]
    )
    
def create_filter_box(title, options, placeholder, component_id=None, value=None):
    return html.Div(className='filter-box', style={'padding': '10px'}, children=[
        html.P(title, style={'fontWeight': 'bold', 'marginBottom': '5px', 'color': '#d1d5db', 'fontSize': '0.9em'}), 
        dcc.Dropdown(id=component_id if component_id else '', options=options, placeholder=placeholder, value=value, clearable=False)
    ])

def get_side_panel_content_for_index(index):
    """Returns the correct side panel content based on the KPI index."""
    if index == 5: # Automatismo aggregation chart
        return html.Div([
            create_filter_box(
                "Agrupamento", 
                options=[{'label': k, 'value': k} for k in automation_stacked_data.keys()],
                placeholder="Selecione...",
                component_id='automatismo-agg-dropdown',
                value='Tipo de Documento'
            )
        ])
    if index == 2: # Captura aggregation chart
        return html.Div([
            create_filter_box(
                "Agrupamento", 
                options=[{'label': k, 'value': k} for k in captura_stacked_data.keys()],
                placeholder="Selecione...",
                component_id='captura-agg-dropdown',
                value='Tipo de Documento'
            )
        ])
    # Default filter content for other KPIs
    return html.Div([
        html.P("Filtros Padrão", style={'fontWeight': 'bold', 'marginTop': '10px', 'fontSize': '0.8em', 'color': '#d1d5db'}), 
        dcc.Dropdown(options=['Opção A', 'Opção B']),
    ], style={'padding': '10px'})

def get_side_panel_info_content():
    return html.Div([
        html.P("Descrição do KPI:", style={'fontWeight': 'bold', 'padding': '10px 10px 0 10px', 'color': '#d1d5db'}),
        dcc.Textarea(
            value='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor.',
            style={'width': '90%', 'height': 100, 'margin': '0 10px', 'backgroundColor': '#374151', 'color': '#d1d5db', 'border': '1px solid #4b5563'}
        )
    ])

# --- Tab Styling ---
tab_style = {'border': '1px solid #4b5563', 'padding': '10px', 'fontWeight': 'bold', 'textTransform': 'capitalize', 'borderRadius': '15px 15px 0 0', 'backgroundColor': '#1f2937', 'color': '#d1d5db'}
selected_tab_style = {'border': '1px solid #8B5CF6', 'borderBottom': '1px solid #1f2937', 'padding': '10px', 'fontWeight': 'bold', 'textTransform': 'capitalize', 'borderRadius': '15px 15px 0 0', 'backgroundColor': '#8B5CF6', 'color': 'white'}


# --- App Layout ---
app.layout = html.Div(style={'fontFamily': 'Inter, sans-serif', 'backgroundColor': '#111827', 'padding': '20px', 'color': '#d1d5db'}, children=[
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='sidebar-state', data={'isOpen': False}),
    dcc.Store(id='table-columns-store', data={'visible_columns': analytic_table_columns}),
    dcc.Store(id='task-table-columns-store', data={'visible_columns': task_analytic_columns}),
    dcc.Store(id='divergence-table-columns-store', data={'visible_columns': divergence_analytic_columns}),
    dcc.Store(id='open-notes-table-columns-store', data={'visible_columns': open_notes_analytic_columns}),
    dcc.Store(id='leadtime-table-columns-store', data={'visible_columns': leadtime_analytic_columns}),

    # --- Column Configuration Modals ---
    dbc.Modal(id='config-modal', size="lg", is_open=False, children=[
        dbc.ModalHeader("Configurar Colunas da Tabela Analítica (Captura)"),
        dbc.ModalBody(dcc.Checklist(id='column-checklist', options=[{'label': col, 'value': col} for col in analytic_table_columns], value=analytic_table_columns, labelStyle={'display': 'block', 'marginBottom': '5px'})),
        dbc.ModalFooter([dbc.Button("Salvar", id="save-config-button", className="mr-1", style={'backgroundColor': '#8B5CF6', 'borderColor': '#8B5CF6'}), dbc.Button("Fechar", id="close-config-button")])]),
    
    dbc.Modal(id='task-config-modal', size="lg", is_open=False, children=[
        dbc.ModalHeader("Configurar Colunas da Tabela de Tarefas (Automatismo)"),
        dbc.ModalBody(dcc.Checklist(id='task-column-checklist', options=[{'label': col, 'value': col} for col in task_analytic_columns], value=task_analytic_columns, labelStyle={'display': 'block', 'marginBottom': '5px'})),
        dbc.ModalFooter([dbc.Button("Salvar", id="save-task-config-button", className="mr-1", style={'backgroundColor': '#8B5CF6', 'borderColor': '#8B5CF6'}), dbc.Button("Fechar", id="close-task-config-button")])]),

    dbc.Modal(id='divergence-config-modal', size="lg", is_open=False, children=[
        dbc.ModalHeader("Configurar Colunas da Tabela de Divergências"),
        dbc.ModalBody(dcc.Checklist(id='divergence-column-checklist', options=[{'label': col, 'value': col} for col in divergence_analytic_columns], value=divergence_analytic_columns, labelStyle={'display': 'block', 'marginBottom': '5px'})),
        dbc.ModalFooter([dbc.Button("Salvar", id="save-divergence-config-button", className="mr-1", style={'backgroundColor': '#8B5CF6', 'borderColor': '#8B5CF6'}), dbc.Button("Fechar", id="close-divergence-config-button")])]),

    dbc.Modal(id='open-notes-config-modal', size="lg", is_open=False, children=[
        dbc.ModalHeader("Configurar Colunas da Tabela de Notas em Aberto"),
        dbc.ModalBody(dcc.Checklist(id='open-notes-column-checklist', options=[{'label': col, 'value': col} for col in open_notes_analytic_columns], value=open_notes_analytic_columns, labelStyle={'display': 'block', 'marginBottom': '5px'})),
        dbc.ModalFooter([dbc.Button("Salvar", id="save-open-notes-config-button", className="mr-1", style={'backgroundColor': '#8B5CF6', 'borderColor': '#8B5CF6'}), dbc.Button("Fechar", id="close-open-notes-config-button")])]),

    dbc.Modal(id='leadtime-config-modal', size="lg", is_open=False, children=[
        dbc.ModalHeader("Configurar Colunas da Tabela de Leadtime"),
        dbc.ModalBody(dcc.Checklist(id='leadtime-column-checklist', options=[{'label': col, 'value': col} for col in leadtime_analytic_columns], value=leadtime_analytic_columns, labelStyle={'display': 'block', 'marginBottom': '5px'})),
        dbc.ModalFooter([dbc.Button("Salvar", id="save-leadtime-config-button", className="mr-1", style={'backgroundColor': '#8B5CF6', 'borderColor': '#8B5CF6'}), dbc.Button("Fechar", id="close-leadtime-config-button")])]),

    # --- Header ---
    html.Div(style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'flex-start', 'position': 'relative', 'marginBottom': '10px'}, children=[
        html.Button(html.I(className="fas fa-filter"), id='open-sidebar-button', n_clicks=0, style={'backgroundColor': '#a486cc', 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'width': '44px', 'height': '44px', 'fontSize': '20px', 'cursor': 'pointer'})]),

    # --- Tabs ---
    dcc.Tabs(id="tabs", value='tab-resumo', children=[
        dcc.Tab(label='Resumo', value='tab-resumo', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Captura', value='tab-captura', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Automatismo', value='tab-automatismo', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Divergências', value='tab-divergencias', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Notas em Aberto', value='tab-notas-aberto', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Leadtime', value='tab-leadtime', style=tab_style, selected_style=selected_tab_style),
    ], style={'height': '44px'}),
    
    # --- Main Content Area ---
    html.Div(style={'display': 'flex', 'marginTop': '20px'}, children=[
        html.Div(id='sidebar', style={'width': '0px', 'padding': '0', 'backgroundColor': '#1f2937', 'borderRight': '1px solid #4b5563', 'overflowX': 'hidden', 'transition': 'width 0.3s ease-in-out'}, children=[
             html.Div(style={'padding': '20px 10px'}, children=[
                html.H3("Filtros", style={'textAlign': 'center', 'color': '#d1d5db'}),
                create_filter_box('Data de Criação', [{'label': 'Últimos 7 dias', 'value': '7d'}, {'label': 'Últimos 30 dias', 'value': '30d'}], 'Selecione...'),
                create_filter_box('Data de Emissão', [{'label': 'Este Mês', 'value': 'this_month'}, {'label': 'Mês Passado', 'value': 'last_month'}], 'Selecione...'),
                create_filter_box('Tipo do Documento', [{'label': 'NFS-e', 'value': 'nfse'}, {'label': 'CT-e', 'value': 'cte'}], 'Selecione...'),
                create_filter_box('Unidade de Negócio', [{'label': 'Unidade 1', 'value': '1'}, {'label': 'Unidade 2', 'value': '2'}], 'Selecione...'),
            ])]),
        html.Div(id='main-content', style={'width': '100%', 'paddingLeft': '20px', 'transition': 'width 0.3s ease-in-out'}, children=[
            html.Div(id='tabs-content')
        ])
    ])
])

# --- TAB LAYOUT FUNCTIONS ---
def create_stories_layout():
    
    ingresso_mensal_data = get_ingresso_mensal()
    ingresso_total_data = get_ingresso_total()
    
    # --- Story 1 ---
    story1 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}, children=[
        dcc.Store(id={'type': 'panel-state', 'index': 1}, data={'visible': False, 'content': None}),
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
                create_captura_kpi_layout(ingresso_total_data),
                dcc.Graph(
                    figure=create_bar_line_chart(
                        ingresso_mensal_data,         # Use the LIVE data here
                        ['totalCount'],    # Match the keys returned by your API
                        'autoPct', 
                        ['#592a9e'], 
                        '#ff5a00', 
                        'Volume Total vs. % de Automação',
                        bar_names=['Total de Notas'],
                        line_name='Percentual de Automatismo'
                    ),
                #dcc.Graph(
                #    figure=create_bar_line_chart(
                #        monthly_data, 
                #        ['total'], 
                #        'auto_pct', 
                #        ['#592a9e'], 
                #        '#ff5a00', 
                #        'Volume Total vs. % de Automação',
                #        bar_names=['Total de Notas'],
                #        line_name='Percentual de Automatismo'
                #    ), 
                    config={'displayModeBar': False},
                    style={'height': '350px'}
                )
            ]),
            html.Div(id={'type': 'side-panel', 'index': 1}, style={'width': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out'}),
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'padding': '0 10px'}, children=[
                html.Button(html.I(className="fas fa-cog"), id={'type': 'filter-button', 'index': 1}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'marginBottom': '15px', 'color': '#d1d5db'}),
                html.Button(html.I(className="fas fa-info-circle"), id={'type': 'info-button', 'index': 1}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
            ]),
        ])
    ])

    # --- Story 2 ---
    story2 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}, children=[
        dcc.Store(id={'type': 'panel-state', 'index': 2}, data={'visible': False, 'content': None}),
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '2fr 1fr', 'gap': '20px'}, children=[
                dcc.Graph(
                    id='captura-stacked-chart',
                    figure=create_stacked_bar_chart(
                        data=captura_stacked_data['Tipo de Documento'],
                        x_key='Category',
                        y_keys=['Captura Automática', 'Email', 'Inserção Manual'],
                        colors=['#592a9e', '#a486cc', '#c4b5fd'],
                        title='Composição do Ingresso por Tipo de Documento'
                    ),
                    config={'displayModeBar': False}, 
                    style={'height': '400px'}
                ),
                dcc.Graph(
                    id='captura-pie-chart',
                    figure=create_pie_chart(['Serviço', 'Material', 'Transporte', 'Concessionárias'], [11150, 7900, 5050, 1510], ['#00b894', '#636e72', '#fdcb6e', '#d63031'], 'Distribuição por Tipo de Nota'), 
                    config={'displayModeBar': False}, style={'height': '400px'}
                )
            ]),
            html.Div(id={'type': 'side-panel', 'index': 2}, style={'width': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out'}),
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'padding': '0 10px'}, children=[
                html.Button(html.I(className="fas fa-cog"), id={'type': 'filter-button', 'index': 2}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'marginBottom': '15px', 'color': '#d1d5db'}),
                html.Button(html.I(className="fas fa-info-circle"), id={'type': 'info-button', 'index': 2}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
            ]),
        ])
    ])
    
    # --- Story 3 ---
    fornecedores_data = get_fornecedores_data()
    prefeituras_data = get_prefeituras_data()

    story3 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}, children=[
        dcc.Store(id={'type': 'panel-state', 'index': 3}, data={'visible': False, 'content': None}),
        dcc.Store(id={'type': 'sort-state', 'table_id': 'fornecedores'}, data={'col': 'Total de Notas', 'order': 'desc'}),
        dcc.Store(id={'type': 'sort-state', 'table_id': 'prefeituras'}, data={'col': 'Total de Notas', 'order': 'desc'}),
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-info-circle"), id={'type': 'info-button', 'index': 3}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
                create_styled_list_table("Top Fornecedores", fornecedores_data, "Razão Social Fornecedor", ["Total de Notas", "Percentual de Ingresso Manual"], 'fornecedores'),
                create_styled_list_table("Top Prefeituras", prefeituras_data, "Prefeitura", ["Total de Notas", "Percentual de Ingresso Manual"], 'prefeituras')
            ]),
            html.Div(id={'type': 'side-panel', 'index': 3}, style={'width': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out', 'backgroundColor': '#111827'}),
        ])
    ])
    
    # --- Story 4 ---
    story4 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}, children=[
        dcc.Store(id={'type': 'panel-state', 'index': 4}, data={'visible': False, 'content': None}),
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-cog"), id='open-config-button', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'marginRight': '15px', 'color': '#d1d5db'}),
            html.Button(html.I(className="fas fa-info-circle"), id={'type': 'info-button', 'index': 4}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
        ]),
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            dcc.Graph(id='analytic-table-graph', style={'flex': '1'}),
            html.Div(id={'type': 'side-panel', 'index': 4}, style={'width': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out', 'backgroundColor': '#111827'}),
        ])
    ])

    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        story1, story2, story3, story4
    ])

def create_automatismo_layout():
    """Builds the entire layout for the Automatismo tab."""
    
    manual_tasks_modal = dbc.Modal([
            dbc.ModalHeader("Configurar Tarefas Manuais"),
            dbc.ModalBody([
                html.P("Selecione as tarefas a serem consideradas no cálculo de 'Com Intervenção Manual'."),
                dcc.Checklist(
                    id='manual-task-checklist',
                    options=[{'label': task, 'value': task} for task in manual_task_names],
                    value=manual_task_names, 
                    labelStyle={'display': 'block', 'margin-bottom': '10px'}
                )
            ]),
            dbc.ModalFooter(dbc.Button("Fechar", id="close-manual-task-modal", className="ml-auto"))
        ], id="modal-manual-tasks", is_open=False)

    story1 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        manual_tasks_modal,
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
                create_automatismo_kpi_layout(),
                html.Div(style={'position': 'relative'}, children=[
                    dcc.Graph(
                        id='monthly-automation-chart',
                        figure=create_bar_line_chart(
                            monthly_automation_data, ['Sem Intervenção Manual', 'Com Intervenção Manual'], 'auto_pct',
                            ['#2dd4bf', '#fb923c'], '#a78bfa', 'Evolução Mensal do Automatismo'
                        ), config={'displayModeBar': False}, style={'height': '350px'}
                    ),
                    html.Button(html.I(className="fas fa-cog"), id='open-manual-task-modal', n_clicks=0, 
                                style={'position': 'absolute', 'top': '10px', 'right': '10px', 'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
                ])
            ])
        ])
    ])

    story2 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        dcc.Store(id={'type': 'panel-state', 'index': 5}, data={'visible': False, 'content': None}),
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': 1, 'display': 'grid', 'gridTemplateColumns': '2fr 1fr', 'gap': '20px'}, children=[
                dcc.Graph(
                    id='automation-agg-chart',
                    figure=create_stacked_bar_chart(
                        data=automation_stacked_data['Tipo de Documento'],
                        x_key='Category',
                        y_keys=['Sem Intervenção Manual', 'Com Intervenção Manual'],
                        colors=['#2dd4bf', '#fb923c'],
                        title='Composição da Intervenção por Tipo de Documento'
                    ),
                    config={'displayModeBar': False}, 
                    style={'height': '400px'}
                ),
                dcc.Graph(
                    figure=create_pie_chart(['Tarefas Manuais', 'Tarefas Automáticas'], [40, 60], ['#fb923c', '#2dd4bf'], 'Distribuição de Tarefas', hole=0.5), 
                    config={'displayModeBar': False}
                )
            ]),
            html.Div(id={'type': 'side-panel', 'index': 5}, style={'width': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out'}),
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'padding': '0 10px'}, children=[
                html.Button(html.I(className="fas fa-cog"), id={'type': 'filter-button', 'index': 5}, n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'}),
            ]),
        ])
    ])

    story3 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
            create_styled_list_table("Top Tarefas Manuais", get_top_manual_tasks_data(), "Tarefa", ["Ocorrências", "Tempo Médio (horas)"], 'top-tasks'),
            create_styled_list_table("Top Analistas", get_top_analysts_data(), "Analista", ["Tarefas Concluídas", "Tempo Médio (min)"], 'top-analysts')
        ])
    ])

    story4 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-cog"), id='open-task-config-button', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'})
        ]),
        dcc.Graph(id='task-analytic-table-graph', style={'width': '100%'})
    ])

    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        story1, story2, story3, story4
    ])

def create_divergencias_layout():
    story1 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
                create_divergencias_kpi_layout(),
                dcc.Graph(
                    figure=create_bar_line_chart(
                        get_monthly_divergence_data(), 
                        ['Notas com Divergência'], 
                        'pct_divergence', 
                        ['#fb923c'], 
                        '#f87171', 
                        'Evolução Mensal de Divergências',
                        line_name='% de Divergência'
                    ), 
                    config={'displayModeBar': False}, style={'height': '350px'}
                )
            ])
        ])
    ])

    story2 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '2fr 1fr', 'gap': '20px'}, children=[
                dcc.Graph(
                    figure=create_simple_bar_chart(
                        pd.DataFrame(divergence_type_data['Tipo de Divergência']),
                        x_key='Category',
                        y_key='Ocorrências',
                        color='#fb923c',
                        title='Ocorrências por Tipo de Divergência'
                    ),
                    config={'displayModeBar': False}, style={'height': '400px'}
                ),
                dcc.Graph(
                    figure=create_pie_chart(
                        [d['Category'] for d in divergence_type_data['Tipo de Divergência']], 
                        [d['Ocorrências'] for d in divergence_type_data['Tipo de Divergência']], 
                        ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#22c55e'], 
                        'Distribuição Percentual de Divergências', hole=0.5
                    ), 
                    config={'displayModeBar': False}, style={'height': '400px'}
                )
            ]),
        ])
    ])

    story3 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        create_styled_list_table(
            "Top Fornecedores com Divergências", 
            get_top_divergence_suppliers_data(), 
            "Fornecedor", 
            ["Notas com Divergência", "Valor Total (R$)"], 
            'top-divergence-suppliers'
        )
    ])

    story4 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-cog"), id='open-divergence-config-button', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'})
        ]),
        dcc.Graph(id='divergence-analytic-table-graph', style={'width': '100%'})
    ])

    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        story1, story2, story3, story4
    ])

def create_notas_aberto_layout():
    story1 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
                create_notas_aberto_kpi_layout(),
                dcc.Graph(
                    figure=create_simple_bar_chart(
                        pd.DataFrame(open_notes_aging_data),
                        x_key='Faixa de Atraso',
                        y_key='Quantidade',
                        color='#facc15',
                        title='Aging de Notas em Aberto'
                    ), 
                    config={'displayModeBar': False}, style={'height': '350px'}
                )
            ])
        ])
    ])

    story2 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': 1, 'display': 'grid', 'gridTemplateColumns': '2fr 1fr', 'gap': '20px'}, children=[
                dcc.Graph(
                    figure=create_stacked_bar_chart(
                        data=open_notes_by_status_data['Unidade de Negócio'],
                        x_key='Category',
                        y_keys=['Aprovação Pendente', 'Análise Fiscal', 'Aguardando Pedido'],
                        colors=['#facc15', '#fbbf24', '#f59e0b'],
                        title='Notas em Aberto por Etapa e Unidade'
                    ),
                    config={'displayModeBar': False}, style={'height': '400px'}
                ),
                dcc.Graph(
                    figure=create_pie_chart(['Aprovação Pendente', 'Análise Fiscal', 'Aguardando Pedido'], [3500, 1850, 1450], ['#facc15', '#fbbf24', '#f59e0b'], 'Distribuição por Etapa', hole=0.5), 
                    config={'displayModeBar': False}
                )
            ]),
        ])
    ])
    
    story3 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        create_styled_list_table(
            "Top Fornecedores com Notas em Aberto", 
            get_top_pending_suppliers_data(), 
            "Fornecedor", 
            ["Notas em Aberto", "Valor em Aberto (R$)"], 
            'top-pending-suppliers'
        )
    ])
    
    story4 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-cog"), id='open-open-notes-config-button', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'})
        ]),
        dcc.Graph(id='open-notes-analytic-table-graph', style={'width': '100%'})
    ])

    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        story1, story2, story3, story4
    ])

def create_leadtime_layout():
    story1 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': '1', 'display': 'grid', 'gridTemplateColumns': '1fr 2fr', 'gap': '20px'}, children=[
                create_leadtime_kpi_layout(),
                dcc.Graph(
                    figure=create_multi_line_chart(
                        get_monthly_leadtime_data(),
                        'Month',
                        ['Leadtime Médio (dias)', 'Leadtime com Divergência (dias)', 'Leadtime sem Divergência (dias)'],
                        ['#60a5fa', '#fb923c', '#2dd4bf'],
                        'Evolução Mensal do Leadtime',
                        'Leadtime (dias)'
                    ), 
                    config={'displayModeBar': False}, style={'height': '350px'}
                )
            ])
        ])
    ])
    
    story2 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
         html.Div(style={'display': 'flex', 'alignItems': 'stretch'}, children=[
            html.Div(style={'flex': 1}, children=[
                dcc.Graph(
                    figure=create_simple_bar_chart(
                        pd.DataFrame(leadtime_by_step_data),
                        y_key='Etapa',
                        x_key='Tempo Médio (dias)',
                        color='#60a5fa',
                        title='Tempo Médio por Etapa do Processo (Bottlenecks)',
                        orientation='h'
                    ),
                    config={'displayModeBar': False}, style={'height': '400px'}
                )
            ])
        ])
    ])
    
    story3 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        # Placeholder for another story, can add more detailed breakdown tables here
        html.H4("Análise Detalhada do Leadtime", style={'textAlign': 'center'}),
        html.P("Esta seção pode incluir tabelas de leadtime por analista, por tipo de divergência, etc.", style={'textAlign': 'center'})
    ])

    story4 = html.Div(style={'backgroundColor': '#1f2937', 'borderRadius': '8px', 'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'end', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
            html.Button(html.I(className="fas fa-cog"), id='open-leadtime-config-button', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontSize': '20px', 'color': '#d1d5db'})
        ]),
        dcc.Graph(id='leadtime-analytic-table-graph', style={'width': '100%'})
    ])

    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        story1, story2, story3, story4
    ])

# --- MAIN CALLBACK TO RENDER TAB CONTENT ---
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-resumo':
        return html.Iframe(srcDoc=html_homepage_content, style={'width': '100%', 'height': '2500px', 'border': 'none'})
    elif tab == 'tab-captura':
        return create_stories_layout()
    elif tab == 'tab-automatismo':
        return create_automatismo_layout()
    elif tab == 'tab-divergencias':
        return create_divergencias_layout()
    elif tab == 'tab-notas-aberto':
        return create_notas_aberto_layout()
    elif tab == 'tab-leadtime':
        return create_leadtime_layout()
    else:
        return html.Div(f"Content for {tab}")

# --- GENERAL APP CALLBACKS (Sidebar, Navigation) ---
@app.callback(
    Output('sidebar', 'style'),
    Output('main-content', 'style'),
    Output('sidebar-state', 'data'),
    Input('open-sidebar-button', 'n_clicks'),
    State('sidebar-state', 'data'),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, data):
    is_open = data['isOpen']
    sidebar_width = '280px'
    
    if is_open:
        sidebar_style = {'width': '0px', 'padding': '0', 'backgroundColor': '#1f2937', 'borderRight': '1px solid #4b5563', 'overflowX': 'hidden', 'transition': 'width 0.3s ease-in-out'}
        content_style = {'width': '100%', 'paddingLeft': '20px', 'transition': 'width 0.3s ease-in-out'}
        new_data = {'isOpen': False}
    else:
        sidebar_style = {'width': sidebar_width, 'padding': '0', 'backgroundColor': '#1f2937', 'borderRight': '1px solid #4b5563', 'overflowX': 'hidden', 'transition': 'width 0.3s ease-in-out'}
        content_style = {'width': f'calc(100% - {sidebar_width})', 'paddingLeft': '20px', 'transition': 'width 0.3s ease-in-out'}
        new_data = {'isOpen': True}
    return sidebar_style, content_style, new_data

@app.callback(
    Output({'type': 'side-panel', 'index': MATCH}, 'children'),
    Output({'type': 'side-panel', 'index': MATCH}, 'style'),
    Output({'type': 'panel-state', 'index': MATCH}, 'data'),
    Input({'type': 'filter-button', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'info-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'panel-state', 'index': MATCH}, 'data'),
    State({'type': 'filter-button', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def toggle_kpi_side_panel(filter_clicks, info_clicks, data, button_id_dict):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        return dash.no_update, dash.no_update, dash.no_update

    prop_id = ctx.triggered[0]['prop_id']
    clicked_button_type = 'filter' if 'filter-button' in prop_id else 'info'
    
    is_visible = data['visible']
    current_content = data['content']

    visible_style = {'width': '250px', 'padding': '10px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out', 'backgroundColor': '#111827'}
    hidden_style = {'width': '0px', 'padding': '0px', 'overflow': 'hidden', 'transition': 'width 0.3s ease-in-out'}

    if not is_visible:
        new_state = {'visible': True, 'content': clicked_button_type}
        new_style = visible_style
        new_children = get_side_panel_content_for_index(button_id_dict['index']) if clicked_button_type == 'filter' else get_side_panel_info_content()
    else:
        if clicked_button_type == current_content:
            new_state = {'visible': False, 'content': None}
            new_style = hidden_style
            new_children = None
        else:
            new_state = {'visible': True, 'content': clicked_button_type}
            new_style = visible_style
            new_children = get_side_panel_content_for_index(button_id_dict['index']) if clicked_button_type == 'filter' else get_side_panel_info_content()
    
    return new_children, new_style, new_state

@app.callback(Output('tabs', 'value'), Input('url', 'pathname'))
def update_active_tab(pathname):
    path_map = {
        '/captura': 'tab-captura',
        '/tarefas': 'tab-automatismo',
        '/divergencias': 'tab-divergencias',
        '/notas-em-aberto': 'tab-notas-aberto',
        '/leadtime': 'tab-leadtime',
    }
    return path_map.get(pathname, 'tab-resumo')

# --- MODAL AND TABLE CALLBACKS ---
@app.callback(
    Output('config-modal', 'is_open'),
    [Input('open-config-button', 'n_clicks'), Input('close-config-button', 'n_clicks'), Input("save-config-button", "n_clicks")],
    [State('config-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_captura_modal(n_open, n_close, n_save, is_open):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        return is_open
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "open-config-button":
        return not is_open
    
    return False

@app.callback(
    Output('task-config-modal', 'is_open'),
    [Input('open-task-config-button', 'n_clicks'), Input('close-task-config-button', 'n_clicks'), Input("save-task-config-button", "n_clicks")],
    [State('task-config-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_task_modal(n_open, n_close, n_save, is_open):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        return is_open
        
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "open-task-config-button":
        return not is_open
        
    return False

@app.callback(
    Output('divergence-config-modal', 'is_open'),
    [Input('open-divergence-config-button', 'n_clicks'), Input('close-divergence-config-button', 'n_clicks'), Input("save-divergence-config-button", "n_clicks")],
    [State('divergence-config-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_divergence_modal(n_open, n_close, n_save, is_open):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']: return is_open
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "open-divergence-config-button": return not is_open
    return False

@app.callback(
    Output('open-notes-config-modal', 'is_open'),
    [Input('open-open-notes-config-button', 'n_clicks'), Input('close-open-notes-config-button', 'n_clicks'), Input("save-open-notes-config-button", "n_clicks")],
    [State('open-notes-config-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_open_notes_modal(n_open, n_close, n_save, is_open):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']: return is_open
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "open-open-notes-config-button": return not is_open
    return False
    
@app.callback(
    Output('leadtime-config-modal', 'is_open'),
    [Input('open-leadtime-config-button', 'n_clicks'), Input('close-leadtime-config-button', 'n_clicks'), Input("save-leadtime-config-button", "n_clicks")],
    [State('leadtime-config-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_leadtime_modal(n_open, n_close, n_save, is_open):
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']: return is_open
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "open-leadtime-config-button": return not is_open
    return False

@app.callback(
    Output('table-columns-store', 'data'),
    Input('save-config-button', 'n_clicks'),
    State('column-checklist', 'value'),
    prevent_initial_call=True
)
def update_captura_column_store(n_clicks, selected_columns):
    if n_clicks: return {'visible_columns': selected_columns}
    return dash.no_update

@app.callback(
    Output('task-table-columns-store', 'data'),
    Input('save-task-config-button', 'n_clicks'),
    State('task-column-checklist', 'value'),
    prevent_initial_call=True
)
def update_task_column_store(n_clicks, selected_columns):
    if n_clicks: return {'visible_columns': selected_columns}
    return dash.no_update

@app.callback(
    Output('divergence-table-columns-store', 'data'),
    Input('save-divergence-config-button', 'n_clicks'),
    State('divergence-column-checklist', 'value'),
    prevent_initial_call=True
)
def update_divergence_column_store(n_clicks, selected_columns):
    if n_clicks: return {'visible_columns': selected_columns}
    return dash.no_update
    
@app.callback(
    Output('open-notes-table-columns-store', 'data'),
    Input('save-open-notes-config-button', 'n_clicks'),
    State('open-notes-column-checklist', 'value'),
    prevent_initial_call=True
)
def update_open_notes_column_store(n_clicks, selected_columns):
    if n_clicks: return {'visible_columns': selected_columns}
    return dash.no_update

@app.callback(
    Output('leadtime-table-columns-store', 'data'),
    Input('save-leadtime-config-button', 'n_clicks'),
    State('leadtime-column-checklist', 'value'),
    prevent_initial_call=True
)
def update_leadtime_column_store(n_clicks, selected_columns):
    if n_clicks: return {'visible_columns': selected_columns}
    return dash.no_update

@app.callback(
    Output('analytic-table-graph', 'figure'),
    Input('table-columns-store', 'data')
)
def update_analytic_table(data):
    visible_columns = data.get('visible_columns', analytic_table_columns)
    return create_table(detailed_invoice_data, "Tabela Analítica (Captura)", visible_columns=visible_columns)

@app.callback(
    Output('task-analytic-table-graph', 'figure'),
    Input('task-table-columns-store', 'data')
)
def update_task_analytic_table(data):
    visible_columns = data.get('visible_columns', task_analytic_columns)
    return create_table(detailed_task_data, "Tabela Analítica de Tarefas", visible_columns=visible_columns)

@app.callback(
    Output('divergence-analytic-table-graph', 'figure'),
    Input('divergence-table-columns-store', 'data')
)
def update_divergence_analytic_table(data):
    visible_columns = data.get('visible_columns', divergence_analytic_columns)
    return create_table(detailed_divergence_data, "Tabela Analítica de Divergências", visible_columns=visible_columns)

@app.callback(
    Output('open-notes-analytic-table-graph', 'figure'),
    Input('open-notes-table-columns-store', 'data')
)
def update_open_notes_analytic_table(data):
    visible_columns = data.get('visible_columns', open_notes_analytic_columns)
    return create_table(detailed_open_notes_data, "Tabela Analítica de Notas em Aberto", visible_columns=visible_columns)

@app.callback(
    Output('leadtime-analytic-table-graph', 'figure'),
    Input('leadtime-table-columns-store', 'data')
)
def update_leadtime_analytic_table(data):
    visible_columns = data.get('visible_columns', leadtime_analytic_columns)
    return create_table(detailed_leadtime_data, "Tabela Analítica de Leadtime", visible_columns=visible_columns)
    
@app.callback(
    Output({'type': 'list-table-body', 'table_id': MATCH}, 'children'),
    Output({'type': 'sort-state', 'table_id': MATCH}, 'data'),
    Input({'type': 'sort-btn', 'table_id': MATCH, 'col': ALL}, 'n_clicks'),
    State({'type': 'sort-state', 'table_id': MATCH}, 'data'),
    prevent_initial_call=True
)
def sort_list_table(n_clicks, sort_state):
    ctx = dash.callback_context
    if not ctx.triggered or not any(ctx.triggered_prop_ids.values()):
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered_id
    table_id = triggered_id['table_id']
    sort_col = triggered_id['col']

    new_order = 'desc'
    if sort_state['col'] == sort_col:
        new_order = 'asc' if sort_state['order'] == 'desc' else 'desc'
    
    new_sort_state = {'col': sort_col, 'order': new_order}

    data = []
    if table_id == 'fornecedores':
        data = get_fornecedores_data()
        primary_col, metric_cols = "Razão Social Fornecedor", ["Total de Notas", "Percentual de Ingresso Manual"]
    elif table_id == 'prefeituras':
        data = get_prefeituras_data()
        primary_col, metric_cols = "Prefeitura", ["Total de Notas", "Percentual de Ingresso Manual"]
    elif table_id == 'top-tasks':
        data = get_top_manual_tasks_data()
        primary_col, metric_cols = "Tarefa", ["Ocorrências", "Tempo Médio (horas)"]
    elif table_id == 'top-analysts':
        data = get_top_analysts_data()
        primary_col, metric_cols = "Analista", ["Tarefas Concluídas", "Tempo Médio (min)"]
    elif table_id == 'top-divergence-suppliers':
        data = get_top_divergence_suppliers_data()
        primary_col, metric_cols = "Fornecedor", ["Notas com Divergência", "Valor Total (R$)"]
    elif table_id == 'top-pending-suppliers':
        data = get_top_pending_suppliers_data()
        primary_col, metric_cols = "Fornecedor", ["Notas em Aberto", "Valor em Aberto (R$)"]

    reverse = (new_order == 'desc')
    
    if sort_col in ["Percentual de Ingresso Manual"]:
        sorted_data = sorted(data, key=lambda x: float(x[sort_col].replace('%', '')), reverse=reverse)
    elif sort_col in ["Tempo Médio (horas)"]:
        sorted_data = sorted(data, key=lambda x: float(x[sort_col].replace('h', '')), reverse=reverse)
    elif sort_col in ["Tempo Médio (min)"]:
        sorted_data = sorted(data, key=lambda x: float(x[sort_col].replace('m', '')), reverse=reverse)
    elif sort_col in ["Valor Total (R$)", "Valor em Aberto (R$)"]:
        sorted_data = sorted(data, key=lambda x: float(x[sort_col].replace('R$ ', '').replace('.', '').replace(',', '.')), reverse=reverse)
    else:
        sorted_data = sorted(data, key=lambda x: x[sort_col], reverse=reverse)

    new_rows = [
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '12px 5px', 'borderBottom': '1px solid #374151'}, children=[
            html.P(item[primary_col], style={'flex': '2', 'margin': '0', 'fontSize': '0.9em'}),
            html.P(f"{item[metric_cols[0]]:,}".replace(",", "."), style={'flex': '1', 'textAlign': 'right', 'margin': '0', 'fontWeight': 'bold'}),
            html.P(item[metric_cols[1]], style={'flex': '1', 'textAlign': 'right', 'margin': '0', 'color': '#f59e0b'})
        ]) for item in sorted_data
    ]
    return new_rows, new_sort_state

# --- CHART AND AUTOMATION CALLBACKS ---
@app.callback(
    Output("modal-manual-tasks", "is_open"),
    [Input("open-manual-task-modal", "n_clicks"), Input("close-manual-task-modal", "n_clicks")],
    [State("modal-manual-tasks", "is_open")],
    prevent_initial_call=True,
)
def toggle_manual_task_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@app.callback(
    Output('monthly-automation-chart', 'figure'),
    Input('manual-task-checklist', 'value'),
    prevent_initial_call=True
)
def update_monthly_automation_chart(selected_tasks):
    new_data = get_monthly_automation_data()
    factor = len(selected_tasks) / len(manual_task_names) if selected_tasks else 0
    for month in new_data:
        original_manual = month["Com Intervenção Manual"]
        month["Com Intervenção Manual"] = int(original_manual * factor)
        month["Sem Intervenção Manual"] += int(original_manual * (1 - factor))
        total = month["Sem Intervenção Manual"] + month["Com Intervenção Manual"]
        month["auto_pct"] = (month["Sem Intervenção Manual"] / total * 100) if total > 0 else 0

    return create_bar_line_chart(
        new_data, ['Sem Intervenção Manual', 'Com Intervenção Manual'], 'auto_pct',
        ['#2dd4bf', '#fb923c'], '#a78bfa', 'Evolução Mensal do Automatismo'
    )

@app.callback(
    Output('automation-agg-chart', 'figure'),
    Input('automatismo-agg-dropdown', 'value')
)
def update_automation_aggregation_chart(selected_group):
    if not selected_group:
        selected_group = 'Tipo de Documento' 

    data_to_plot = automation_stacked_data[selected_group]
    title = f"Composição da Intervenção por {selected_group}"
    
    return create_stacked_bar_chart(
        data=data_to_plot,
        x_key='Category',
        y_keys=['Sem Intervenção Manual', 'Com Intervenção Manual'],
        colors=['#2dd4bf', '#fb923c'],
        title=title
    )

@app.callback(
    Output('captura-stacked-chart', 'figure'),
    Input('captura-agg-dropdown', 'value')
)
def update_captura_aggregation_chart(selected_group):
    if not selected_group:
        selected_group = 'Tipo de Documento'

    data_to_plot = captura_stacked_data[selected_group]
    title = f"Composição do Ingresso por {selected_group}"

    return create_stacked_bar_chart(
        data=data_to_plot,
        x_key='Category',
        y_keys=['Captura Automática', 'Email', 'Inserção Manual'],
        colors=['#592a9e', '#a486cc', '#c4b5fd'],
        title=title
    )
    
# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)