#!/bin/bash

# Ativa o ambiente virtual (se existir)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar os pacotes necessários para rodar o WSGI assíncrono
echo "Verificando dependências do servidor WSGI..."
pip install gunicorn gevent

echo ""
echo "🚀 Iniciando o Dash com Gunicorn (4 Workers + Gevent) na porta 8050..."
echo "Acesse: http://localhost:8050/?customer=cliente_xyz"
echo ""

# Muda para a pasta modules temporariamente e roda o gunicorn
# -w 4: 4 processos independentes para suportar acesso concorrente.
# -k gevent: Workers assíncronos (ótimo para chamadas IO e API como as feitas aqui).
# app:server: Procura a variável "server" (o Flask interno) no arquivo "app.py".
cd modules && gunicorn -w 4 -k gevent app:server -b 0.0.0.0:8050
