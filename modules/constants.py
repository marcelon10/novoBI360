HTML_HOMEPAGE_CONTENT = """<!DOCTYPE html>
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